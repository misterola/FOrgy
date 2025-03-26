from pathlib import Path
import os
import shutil
from forgy.messyforg import(
    check_internet_connection,
    create_directories,
    fetch_book_metadata,
)
from forgy.filesystem_utils import copy_directory_files, get_files_from_sources
from forgy.metadata_search import get_book_covers
from forgy.database import get_all_metadata, create_db_and_table
from forgy.logger import configure_logger

logger = configure_logger('main')

logger.info("This is the initial")

move_metadata = False
get_cover_pics=True
get_metadata_dict=True

def main():  # specify how to get sources
    [data_path,
    pdfs_path,
    missing_isbn_path,
    missing_metadata_path,
    book_metadata_path,
    extracted_texts_path,
    cover_pics_path] = create_directories(
                            data="data",
                            forgy_pdfs_copy="pdfs",
                            missing_isbn="missing_isbn",
                            missing_metadata="missing_metadata",
                            book_metadata="book_metadata",
                            extracted_texts="extracted_texts",
                            book_covers="book_covers"
                        )
    create_db_and_table(book_metadata_path, table_name="Books", db_name="library.db", delete_table=True)

    db_path = f"{book_metadata_path}/library.db"

    user_pdfs_src= Path(r'C:\Users\Ola\Desktop\forgy_test_folder\ubooks')

    forgy_pdfs_copy= pdfs_path    # book_metadata_path # r"C:\Users\Ola\Desktop\newer"

    user_pdfs_destination = Path(r'C:\Users\Ola\Desktop\data')
    #get_src_and_dst(src, dst, directory_list_src=True, directory_tree_src=False)

    copy_directory_files(user_pdfs_src, forgy_pdfs_copy)


    fetch_book_metadata(user_pdfs_src, forgy_pdfs_copy, user_pdfs_destination, db_path,  missing_isbn_path, missing_metadata_path, extracted_texts_path, table_name="Books")



    if get_cover_pics:
        get_book_covers(cover_pics_path, db_path, "Books")


    if get_metadata_dict:
        # metadata_dictionary coverted to str to enable .write() work on it
        metadata_dictionary = str(get_all_metadata(db_path, "Books"))
        with open(f"{Path(book_metadata_path)}/metadata_dictionary.txt", 'w') as metadata_dict_text:
            metadata_dict_text.write(metadata_dictionary)
            print("metadata_dictionary text created successfully")


    if not move_metadata:
        try:
            shutil.copytree(data_path, user_pdfs_destination, dirs_exist_ok=True)
            logger.info(f"Source directory {data_path} copied to {user_pdfs_destination} successfully")
        except Exception as e:
            logger.exception(f"Exception {e} raised")
            # print(f"Exception {e} raised")
            pass
    else:
        # TODO: debug: move_metadata=True
        try:
            shutil.copytree(data_path, user_pdfs_destination, dirs_exist_ok=True)
            os.rmdir(data_path)
            logger.info(f"Source directory {data_path} moved to {user_pdfs_destination} successfully")
        except Exception as e:
            logger.exception(f"Exception {e} raised")
            pass

    
        
        
if __name__=='__main__':
    if check_internet_connection():
        main()
    else:
        print("Internet is unavailable")
        
