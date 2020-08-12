import glob
import os
import zipfile
import shutil 

from django.views.generic.edit import FormView
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files import File 

from uploads.core.models import Document
from uploads.core.forms import DocumentForm

from uploads.core.business_logic.match_face import *

from django import forms
from multiupload.fields import MultiFileField

from .forms import UploadForm
from .models import Attachment

class UploadView(FormView):

    template_name = 'core/simple_upload.html'
    form_class = UploadForm
    uploaded_photo = ''
    list_images = []
    zip_file = ''
    error = False

    def get_context_data(self, **kwargs):
        '''
        Overrides context data and setups context variables to be passed to the view
        '''

        context = super(UploadView, self).get_context_data(**kwargs)
        context['uploaded_file_url'] = self.uploaded_photo
        context['list_images'] = self.list_images
        context['zip_file'] = self.zip_file
        context['error'] = self.error
        return context

    def form_valid(self, form):
        '''
        Check if form is valid and processes images
        '''
        if self.request.method=='POST' and 'process_btn' in self.request.POST:

            # Images
            uploaded_images = form.cleaned_data['attachments']
            clean_dir('media/attachments/*')
            clean_dir('media/*')
            
            try:
                # Cleans archive dir it it exists
                shutil.rmtree('media/arch_files')
            except:
                pass

            # Processes only one image
            if len(uploaded_images) == 1:

                myfile = form.cleaned_data['attachments'][0]
                path = default_storage.save('{0}'.format(myfile), ContentFile(myfile.read()))
                
                photos = [photo for photo in glob.glob('media/database/*')]
                match_face_5 = MatchFace(photos, 'media/database/')
                match_face_5.set_desired_face('media/{0}'.format(path))
                
                if match_face_5.validate_photo():

                    self.list_images = match_face_5.process()[:5]
                    self.uploaded_photo = 'media/{0}'.format(path)
                else:

                    self.error = True

            # Processes multiple images
            else:

                self.zip_file = generate_zip(uploaded_images)

        elif self.request.method=='POST' and 'add_db_btn' in self.request.POST:

            add_to_db(form.cleaned_data['attachments'])
            
        return self.render_to_response(self.get_context_data(form=form))


def add_to_db(uploaded_images):

    db_photos = [photo.replace('media/database/', '') for photo in glob.glob('media/database/*')]
    
    for image in uploaded_images:

        if str(image) not in db_photos:
            
            default_storage.save('database/{0}'.format(image), ContentFile(image.read()))

def generate_zip(uploaded_images):
    '''
    Processes multiple images and generate zip folder with them.
    Download button will appear for download
    '''

    photos = [photo for photo in glob.glob('media/database/*')]
    match_face_5 = MatchFace(photos, 'media/database/')

    # Find matches for each uploaded photo
    for desired_photo in uploaded_images:

        myfile = desired_photo
        path = default_storage.save('arch_files/{0}_dir/{1}'.format(myfile, myfile), ContentFile(myfile.read()))
        match_face_5.set_desired_face('media/{0}'.format(path))

        if match_face_5.validate_photo():

            list_images = match_face_5.process()

            for image in list_images:
                
                path = 'media/arch_files/{0}_dir/matches/'.format(myfile)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                shutil.copy(image['photo_path'], path)
        
        else:

            f = open('media/arch_files/{0}_dir/Error.txt'.format(myfile), "w") 
            f.write('Face was not detected on the image: {0}'.format(myfile))
            f.close()

    # Generating zip and saving
    zip_name = 'media/identities'
    directory_name = 'media/arch_files'

    shutil.make_archive(zip_name, 'zip', directory_name)
    shutil.rmtree('media/arch_files')

    return '{0}.zip'.format(zip_name)


def clean_dir(path):
    '''
    Cleans the specified dir
    '''

    for f in glob.glob(path):
        
        if not os.path.isdir(f): os.remove(f)



