import brainimagelibrary
gid = 'g.19'

if brainimagelibrary.dois.collection.exists(gid):
    metadata = brainimagelibrary.dois.collection.get(gid)
    print(brainimagelibrary.dois.collection.get_datasets(gid))
