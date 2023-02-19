let recognizer;

async function predictWord() {
  // Array of words that the recognizer is trained to recognize.
  const words = recognizer.wordLabels();
  recognizer.listen(({scores}) => {
    // Turn scores into a list of (score,word) pairs.
    scores = Array.from(scores).map((s, i) => ({score: s, word: words[i]}));
    // Find the most probable word.
    scores.sort((s1, s2) => s2.score - s1.score);
    document.querySelector('#transcription').textContent = scores[0].word;
  }, {probabilityThreshold: 0.75});
}

async function app() {
  recognizer = speechCommands.create('BROWSER_FFT');
  await recognizer.ensureModelLoaded();
  predictWord();
}

app();

function startRecording() {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.start();

      const audioChunks = [];
      mediaRecorder.addEventListener("dataavailable", event => {
        audioChunks.push(event.data);
      });

      mediaRecorder.addEventListener("stop", () => {
        const audioBlob = new Blob(audioChunks);
        const formData = new FormData();
        formData.append('audio', audioBlob, 'audio.wav');

        fetch('/transcribe', {
          method: 'POST',
          body: formData
        })
        .then(response => response.text())
        .then(transcription => {
          console.log(transcription);
          document.querySelector('#transcription').textContent = transcription;
        });
      });

      setTimeout(() => {
        mediaRecorder.stop();
      }, 5000);
    });
}
