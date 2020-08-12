import dlib
import glob
from skimage import io
from scipy.spatial import distance


class Identity(object):

    def __init__(self, photo_name, photo_path, image, description):

        self.photo_path = photo_path
        self.image = image
        self.description = description
        self.photo_name = photo_name

    def get_photo_name(self):

        return self.photo_name

    def get_photo_path(self):

        return self.photo_path

    def get_image(self):

        return self.image

    def get_description(self):

        return self.description

    def set_accuracy(self, accuracy):

        self.accuracy = accuracy

    def get_accuracy(self):

        return self.accuracy


class MatchFace(object):

    def __init__(self, photos, db_path):

        # Init models
        self.detector = dlib.get_frontal_face_detector()
        self.face_rec_model = dlib.face_recognition_model_v1('uploads/core/models/dlib_face_recognition_resnet_model_v1.dat')
        self.shapes_model = dlib.shape_predictor('uploads/core/models/shape_predictor_5_face_landmarks.dat')

        self.db_path = db_path
        self.identities = [self.get_identity(photo) for photo in photos]
        self.desire_identity = None

    def __call__(self, photos):

        return [self.get_identity(photo) for photo in photos]

    def set_desired_face(self, photo):

        self.desire_identity = self.get_identity(photo)

    def validate_photo(self):

        return self.desire_identity is not None

    def get_identity(self, photo):
        '''
        Loads image and returns identity with a face descriptor
        '''

        try:

            image = io.imread(photo)
            detectors = self.detector(image, 1)

            for _, d in enumerate(detectors):
                print(self.face_rec_model.compute_face_descriptor(image, self.shapes_model(image, d)))
                return Identity(photo.replace(self.db_path, ''), photo, image, self.face_rec_model.compute_face_descriptor(image, self.shapes_model(image, d)))
        except:

            pass

    def find_match(self):
        '''
        Finds matches of the desired photo
        '''
        self.identities = [identity for identity in self.identities if identity is not None]
        for identity in self.identities:

            identity.set_accuracy(distance.euclidean(identity.get_description(), self.desire_identity.get_description()))

        return [identity for identity in self.identities if identity.get_accuracy() < .6]

    def process(self):
        '''
        Returns list of matches
        '''

        matches = self.find_match()

        return [{'photo_name':match.get_photo_name(), 'photo_path':match.get_photo_path(),'accuracy':'{0:.1f}'.format((1 / (1 + match.get_accuracy())) * 100)} for match in matches]