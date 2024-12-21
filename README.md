# FOrgy
FOrgy is a powerful file organizer that automatically detects ISBN from your PDF ebooks, use the detected ISBN to retrieve book metadata, automatically rename these files (if you so desire), and create for you a decent personal  library of your books. FOrgy essentially helps you manage your messy PDF ebook collection, including when the "by their names we shall know them" principle does not strictly apply to your own ebooks.

The name FOrgy is from its capabilities as a File(F)-Organizer-(Org)-built-using-Python (y).






# How it works
You provide links to directories containing your ebooks and FOrgy creates its own local copy of those books, extracts ISBN from each book, retrieves metadata from Google's BookAPI or Openlibrary API, checks file for size, rename files, creates a database of books in your library which you can easily search through. FOrgy also collects books without metadata or isbn into separate folder and further help you local metadata for those otherwise.





