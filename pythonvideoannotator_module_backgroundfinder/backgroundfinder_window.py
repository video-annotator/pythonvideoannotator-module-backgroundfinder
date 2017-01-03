import pyforms, math, cv2
from pysettings import conf
from pyforms import BaseWidget
from pyforms.Controls import ControlDir
from pyforms.Controls import ControlNumber
from pyforms.Controls import ControlList
from pyforms.Controls import ControlCombo
from pyforms.Controls import ControlSlider
from pyforms.Controls import ControlImage
from pyforms.Controls import ControlButton
from pyforms.Controls import ControlCheckBox
from pyforms.Controls import ControlCheckBoxList
from pyforms.Controls import ControlEmptyWidget
from pyforms.Controls import ControlProgress

from mcvgui.dialogs.simple_filter import SimpleFilter
from mcvapi.blobs.order_by_position import combinations

from pythonvideoannotator_models_gui.dialogs.videos_selector import VideosSelectorDialog
from mcvapi.filters.background_detector import BackgroundDetector

import json

class BackgroundFinderWindow(BaseWidget):

	def __init__(self, parent=None):
		super(BackgroundFinderWindow, self).__init__('Background finder', parent_win=parent)
		self.mainwindow = parent

		self.layout().setMargin(5)
		self.setMinimumHeight(400)
		self.setMinimumWidth(400)

		self._panel			= ControlEmptyWidget('Videos')
		self._image 		= ControlImage('Image')
		self._progress  	= ControlProgress('Progress')
		self._apply 		= ControlButton('Apply and close', checkable=True)

		self._matrixSize 	= ControlSlider('Gaussian blur matrix size', 5, 1, 11)
		self._sigmaX 		= ControlSlider('Gaussian blur sigma X', 5, 1, 11)

		self._jump_2_frame  = ControlSlider('Jump n frames', 100, 1, 10000)
		self._cmp_jump 		= ControlSlider('Compare with frame in front', 100, 1, 10000)
		self._threshold 	= ControlSlider('Threshold', 5, 0, 255)

		
		self._formset = [			
			['_panel','||',			
				[
					('_matrixSize', '_sigmaX'),
					('_jump_2_frame', '_cmp_jump', '_threshold'),
					'_image',
				],
			],
			'_apply',
			'_progress'
		]

		self.videos_dialog = VideosSelectorDialog(self)
		self._panel.value = self.videos_dialog

		self._apply.value			= self.__apply_event
		self._apply.icon 			= conf.ANNOTATOR_ICON_PATH

		self._progress.hide()

	def init_form(self):
		super(BackgroundFinderWindow, self). init_form()
		self.videos_dialog.project = self.mainwindow.project
	
	###########################################################################
	### EVENTS ################################################################
	###########################################################################



	###########################################################################
	### PROPERTIES ############################################################
	###########################################################################
	
	
	def __update_image_event(self, frame, frame_count):
		self._image.value = frame
		self._progress.value = self._base_nframes + frame_count

	def __apply_event(self):

		if self._apply.checked and self._apply.label == 'Apply and close':
			self._panel.enabled 		= False
			self._image.enabled 		= False
			self._matrixSize.enabled 	= False
			self._sigmaX.enabled 		= False
			self._jump_2_frame.enabled 	= False
			self._cmp_jump.enabled 		= False
			self._threshold.enabled 	= False

			self._apply.label 			= 'Cancel'

			total_steps = 0
			for video in self.videos_dialog.selected_data: total_steps += video.total_frames

			self._progress.min = 0
			self._progress.max = total_steps
			self._progress.show()

			self._base_nframes = 0
			exit = True
			for video in self.videos_dialog.selected_data:

				if not self._apply.checked:	break
				
				bg = BackgroundDetector(
					capture 				= video.video_capture, 
					gaussianBlurMatrixSize 	= self._matrixSize.value, 
					gaussianBlursigmaX 		= self._sigmaX.value,
					update_function 		= self.__update_image_event
				)

				bg.detect( self._jump_2_frame.value, self._cmp_jump.value, self._threshold.value )
				
				image = video.create_image()
				image.name = 'background-{0}'.format(len(video.images))
				image.image = bg.background_color
				

				self._base_nframes += video.total_frames

			self._panel.enabled 		= True
			self._image.enabled 		= True
			self._matrixSize.enabled 	= True
			self._sigmaX.enabled 		= True
			self._jump_2_frame.enabled 	= True
			self._cmp_jump.enabled 		= True
			self._threshold.enabled 	= True
			self._apply.label 			= 'Apply and close'
			exit 						= self._apply.checked
			self._apply.checked 		= False
			self._progress.hide()

			
			if exit: self.close()





	


if __name__ == '__main__': 
	pyforms.startApp(TrackingWindow)
