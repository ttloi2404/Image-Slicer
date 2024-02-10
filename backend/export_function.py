from interface.progress_bar import run_task_with_progress_bar
import os
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog


def start_exporting(processor):
    output_directory = filedialog.askdirectory()
    if output_directory:
        continue_exporting(processor, output_directory)


@run_task_with_progress_bar
def continue_exporting(processor, output_directory):
    try:
        for entity, name in zip(processor.all_sliced_images, processor.viewer_controller.current_viewer.all_entity_names):
            entity.save(os.path.join(output_directory, name.get()))
        CTkMessagebox(
            master=processor.parent,
            title="Task Completed",
            message="Files successfully exported.",
            icon="check",
            justify="center",
            option_focus=1,
        )
        os.startfile(output_directory)

    except Exception as error:
        CTkMessagebox(
            master=processor.parent,
            title="Task not Completed",
            message=str(error).capitalize(),
            icon="info",
            justify="center",
            option_focus=1,
        )
