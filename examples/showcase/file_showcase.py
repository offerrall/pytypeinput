from pytypeinput import OptionalEnabled, OptionalDisabled, Placeholder, Description, Label, Field, Annotated, File, ImageFile

from visual_test_base import run_visual_test


def file_test(
    basic_file: File,
    
    file_with_label: Annotated[File, Label("Upload Document")],
    
    file_with_description: Annotated[
        File,
        Description("Upload any file type")
    ],
    
    file_full: Annotated[
        File,
        Label("Attachment"),
        Description("Upload a file attachment")
    ],
    
    basic_image: ImageFile,
    
    image_with_label: Annotated[ImageFile, Label("Profile Picture")],
    
    image_with_description: Annotated[
        ImageFile,
        Description("Upload your profile photo (PNG, JPG)")
    ],
    
    image_full: Annotated[
        ImageFile,
        Label("Cover Image"),
        Description("Upload a cover image for your profile (max 5MB)")
    ],
    
    files_list: list[File],
    
    documents_list: Annotated[
        list[File],
        Label("Documents"),
        Description("Upload multiple documents")
    ],
    
    images_list: list[ImageFile],
    
    gallery_images: Annotated[
        list[ImageFile],
        Label("Gallery Images Suu"),
        Description("Upload multiple images for your gallery")
    ],
    
    optional_file: File | None,
    
    optional_image: ImageFile | None,
    
    optional_file_full: Annotated[
        File,
        Label("Optional Attachment"),
        Description("Optional: Attach a file if needed")
    ] | None,
    
    optional_image_full: Annotated[
        ImageFile,
        Label("Optional Avatar"),
        Description("Optional: Upload an avatar image")
    ] | None,
    
    optional_files: list[File] | None,
    
    optional_images: list[ImageFile] | None,
    
    optional_explicit_file: File | OptionalEnabled = None,
    
    optional_disabled_image: ImageFile | OptionalDisabled = None,
):
    pass


if __name__ == "__main__":
    run_visual_test(file_test, "File Types Test - File & ImageFile")