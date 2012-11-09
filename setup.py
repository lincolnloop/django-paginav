from setuptools import setup, find_packages

setup(
    name='django-paginav',
    version='1.0a',
    description=("A Django template pagination navigation tag."),
    author='Chris Beaven',
    author_email='smileychris@gmail.com',
    url='http://github.com/LincolnLoop/django-paginav',
    packages=find_packages(),
    include_package_data=True,
    package_data={'paginav': ['templates/*.*']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
