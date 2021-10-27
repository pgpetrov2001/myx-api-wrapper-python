from myx import Client
c = Client('demo.user@myxrobotics.com', 'testpassword')


def test():
    twins = c.get_twins()
    annots = c.get_annotations('72')
    print(c.make_new_annotation('100', 1, 1, 1, 'pointless annotation', 'google.com', '') )
    print(c.get_annotations('100'))

    #print(twins)
    print(annots)
    f = c.get_file('1', 'report.pdf')

"""
fs = []
names = []
for i in range(1,3):
    names.append(f'sourceImages/Nokia_pilot_1_BGS0521_scan_1_27_03_2021 ({i}).JPG')
    fs.append(c.get_file('1', names[-1]))

j = c.upload_images_from_fs('/home/pgpetrov/Pictures/')
print(j)
c.finish_upload()
"""

print(c.get_annotations('100'))
print(c.make_new_annotation(1, 1, 1, 1, 'asd', 'google.com', 'checkit'))
