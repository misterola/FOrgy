from pathlib import Path

from forgy.messyforg import(
    check_internet_connection,
    create_directories,
    create_db_and_table,
    get_src_and_dst,
    copy_destination_directory,
    fetch_book_metadata
)
from forgy.logger import configure_logger

logger = configure_logger('main')

logger.info("This is the initial")


#database = book_metadata_path/"library.db"
# db_path = book_metadata_path/"library.db"

def main():  # specify how to get sources
    [data_path,
    pdfs_path,
    missing_isbn_path,
    missing_metadata_path,
    book_metadata_path,
    extracted_texts_path,
    cover_pics_path] = create_directories(
                            data="data",
                            pdfs="pdfs",
                            missing_isbn="missing_isbn",
                            missing_metadata="missing_metadata",
                            book_metadata="book_metadata",
                            extracted_texts="extracted_texts",
                            book_covers="book_covers"
                        )
    create_db_and_table(book_metadata_path, table_name="Books", library_db_name="library.db", delete_db_table=True)

    db_path = f"{book_metadata_path}/library.db"

    src= Path(r'C:\Users\Ola\Desktop\forgy_test_folder\ubooks')

    dst= pdfs_path    # book_metadata_path # r"C:\Users\Ola\Desktop\newer"

    #get_src_and_dst(src, dst, directory_list_src=True, directory_tree_src=False)

    copy_destination_directory(src, pdfs_path)

    fetch_book_metadata(pdfs_path, src, db_path,  missing_isbn_path, missing_metadata_path, extracted_texts_path, table_name="Books")

if __name__=='__main__':
    if check_internet_connection():
        main()
    else:
        print("Internet is unavailable")
        
