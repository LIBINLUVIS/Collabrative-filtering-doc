def recommentation(request,pk):
    books=Books.objects.all()
    ratings=Rating.objects.all()
    x=[]
    y=[]
    a=[]
    b=[]
    for item in books:
        x=[item.id,item.ISBN,item.Book_title]
        y+=[x]
    books_df=pd.DataFrame(y,columns=['book_id','ISBN','title'])

    for item in ratings:
        a=[item.user_id,item.isbn,item.rating]
        b+=[a]
    ratings_df=pd.DataFrame(b,columns=['user_id','ISBN','rating'])
    x = ratings_df['user_id'].value_counts() > 1
    y = x[x].index
    ratings = ratings_df[ratings_df['user_id'].isin(y)]
    rating_with_books = ratings.merge(books_df, on='ISBN')
    number_rating = rating_with_books.groupby('title')['rating'].count().reset_index()
    number_rating.rename(columns= {'rating':'number_of_ratings'}, inplace=True)
    final_rating = rating_with_books.merge(number_rating, on='title')
    final_rating = final_rating[final_rating['number_of_ratings'] >= 1]
    final_rating.drop_duplicates(['user_id','title'], inplace=True)
    book_pivot = final_rating.pivot_table(columns='user_id', index='title', values="rating")
    book_pivot.fillna(0, inplace=True)
    book_sparse = csr_matrix(book_pivot)
    model = NearestNeighbors(algorithm='brute')
    model.fit(book_sparse)
    book_title=[]
    user_book_isbn=[]
    user_recom_index=[]
    final_recom=[]
    final_book_obj_unique=[]
    try:
        user_ratings=Rating.objects.filter(user_id=pk).order_by('-id')[0]
        user_book_isbn.append(user_ratings.isbn)
        recommented=[]
        user_latest_rated_book=Books.objects.get(ISBN=user_book_isbn[0])
        book_title.append(user_latest_rated_book.Book_title)
        for i in range(len(book_pivot)):
            if book_pivot.index[i]==book_title[0]:
                user_recom_index.append(i)
                break
        distances, suggestions = model.kneighbors(book_pivot.iloc[user_recom_index[0], :].values.reshape(1, -1))
        for i in range(len(suggestions)):
            recommented.append(book_pivot.index[suggestions[i]])
        res={}
        for x in recommented:
            for i in range(len(recommented[0])):
                book=Books.objects.get(Book_title=x[i])
                res['title']=book.Book_title
                res['Book_author']=book.Book_Author
                res['img']=str(book.img_url_L)
                res_copy=res.copy()
                final_recom.append(res_copy)
    except:
        return Response(final_recom)
    e=[]
    f=[]
    a=[]
    try:
        user_search=savesearch.objects.filter(userid=pk).order_by('-id')[0]
        e.append(user_search.booktitle)
        for i in range(len(book_pivot)):
            if book_pivot.index[i]==e[0]:
                f.append(i)
                break
        distances,suggestions=model.kneighbors(book_pivot.iloc[f[0],:].values.reshape(1,-1))
        for i in range(len(suggestions)):
            a.append(book_pivot.index[suggestions[i]])
        res1={}
        for x in a:
            for i in range(len(a[0])):
                book=Books.objects.get(Book_title=x[i])
                res1['title']=book.Book_title
                res1['Book_author']=book.Book_Author
                res1['img']=str(book.img_url_L)
                res1_copy=res1.copy()
                final_recom.append(res1_copy)
    except:
        return Response(final_recom)

    for i in final_recom:
        if i not in final_book_obj_unique:
            final_book_obj_unique.append(i)

    return Response(final_book_obj_unique)