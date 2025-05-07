# HansiAudioVisualizer

Renders a video of custom visualizations for audio files (MP3). File Selection, settings, etc. are available via a visual web interface.

![Home](/img/Home.png)

Either locally select an audio file from the system or paste a YouTube URL into the form. Additional information will be displayed upon audio selection.

A preview thumbnail for the current settings will be automatically displayed. When everything is set, simply press the "Generate Video" button and the video will be rendered and displayed when finished, where it then can be either played or downloaded.


## Install Dependencies

In root directory:

``npm install``

``cd frontend && npm install``

``cd backend && pip install -r requirements.txt``

Additionally, this project requires [FFmpeg](https://ffmpeg.org/download.html).


### Start

``npm start`` starts frontend and backend server.

Website runs locally on [http://localhost:5173/](http://localhost:5173/)

