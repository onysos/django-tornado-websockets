from tornado_websockets.modules.progress_bar import ProgressBar

module_progress_bar_test = ProgressBar('my_progress_bar', False)

module_progress_bar_indeterminate_test = ProgressBar('my_indeterminate_progress_bar', min=0, max=0)
