from setuptools import setup


install_requires = [
    "Flask>=0.12.2",
    "fastavro>=0.16.4",
    "kafka-python>=1.3.5"
]


setup(
    name="flask-kafka",
    version="0.0.1",
    description="Use kafka in flask quickly",
    url="https://github.com/huangxiaohen2738/flask-kafka",
    download_url="https://github.com/huangxiaohen2738/flask-kafka",
    author="Huang Song",
    author_email="huangxiaohen2738@gmail.com",
    py_modules=["flask_kafka"],
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta"
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Topic :: System :: Networking",
        "Topic :: Terminals",
        "Topic :: Utilities"
    ]
)
