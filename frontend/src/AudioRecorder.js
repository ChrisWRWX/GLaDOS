// import React, { Component } from "react";
import * as React from "react";
import AudioAnalyser from "react-audio-analyser";


const AudioRecorder = (props) => {
  const [status, setStatus] = React.useState();
  const [audioSrc] = React.useState();
  const [audioQueue, setAudioQueue] = React.useState([]);
  const qRef = React.useRef('');
  const [micImage, setMicImage] = React.useState("./mic-32-black.png")
  const audioType = "audio/wav"
  const canvasRef = React.useRef(null);
  const [analyserNode, setAnalyserNode] = React.useState(null);


  React.useEffect(() => {
    qRef.current = audioQueue
  }, [audioQueue])

  const audioProps = {
    width: 200,
    height: 50,
    audioType,
    // audioOptions: {sampleRate: 16000},
    status,
    audioSrc,
    timeslice: 1000, // timeslice（https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder/start#Parameters）
    startCallback: e => {
    },
    pauseCallback: e => {
    },
    stopCallback: e => {
      props.socket.send(e)
      // props.socket.send('start a conversation')
    },
    onRecordCallback: e => {
    },
    errorCallback: err => {
    }
  };

  // makes playing audio return a promise
  function playAudio(audio){
    return new Promise(res=>{
      const audioContext = new AudioContext();
      
      const audioSource = audioContext.createBufferSource()
      const analyserNode = audioContext.createAnalyser()
      
      audioContext.resume();
      audioSource.connect(analyserNode);
      analyserNode.connect(audioContext.destination);

      fetch(audio)
      .then(response => response.arrayBuffer())
      .then(arrayBuffer => audioContext.decodeAudioData(arrayBuffer))
      .then(audioBuffer => {
        audioSource.buffer = audioBuffer;
        audioSource.start();
      });
      
      setAnalyserNode(analyserNode)

      audioSource.onended = res
    })
  }

  React.useEffect(() => {
    const canvas = canvasRef.current;
    const canvasContext = canvas.getContext('2d');

    if (analyserNode != null){
      const drawWaveform = () => {
        requestAnimationFrame(drawWaveform);
    
        const bufferLength = analyserNode.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyserNode.getByteTimeDomainData(dataArray);
    
        canvasContext.fillStyle = 'rgb(0, 0, 0)';
        canvasContext.fillRect(0, 0, canvas.width, canvas.height);
    
        canvasContext.lineWidth = 2;
        canvasContext.strokeStyle = 'rgb(255, 0, 0)';
        canvasContext.beginPath();
    
        const sliceWidth = (canvas.width * 1.0) / bufferLength;
        let x = 0;
    
        for (let i = 0; i < bufferLength; i++) {
          const v = dataArray[i] / 128.0;
          const y = (v * canvas.height) / 2;
    
          if (i === 0) {
            canvasContext.moveTo(x, y);
          } else {
            canvasContext.lineTo(x, y);
          }
    
          x += sliceWidth;
        }
    
        canvasContext.lineTo(canvas.width, canvas.height / 2);
        canvasContext.stroke();
      };
    
      drawWaveform();
    }
    else {
      canvasContext.fillStyle = 'rgb(0, 0, 0)';
      canvasContext.fillRect(0, 0, canvas.width, canvas.height);
      canvasContext.lineWidth = 2;
      canvasContext.strokeStyle = 'rgb(255, 0, 0)';
      canvasContext.beginPath();
    }
  }, [canvasRef, analyserNode]);

  

  props.socket.onmessage = (e) => {    
    const blob = e.data.slice(0, e.data.size, "audio/wav")
    try {
      // setAudioSrc(window.URL.createObjectURL(blob))
      const tempQueue = audioQueue.slice()
      tempQueue.push(blob)
      setAudioQueue(tempQueue)
    }
    catch {
    }
  }

  React.useEffect(() => {
    const queueAudio = async () => {
      if (qRef.current.length > 0){
        const tempQueue = qRef.current.slice();
        const firstElement = tempQueue.shift();
        setAudioQueue(tempQueue)
        await playAudio(window.URL.createObjectURL(firstElement))
        setTimeout(() => queueAudio(), 100)
      }
      else {
        setTimeout(() => queueAudio(), 100);
      }
    }
    
    queueAudio();
  }, [])

  return (
    <>
      <div>
        <button 
          style={{textAlign: 'center'}}
          onClick={() => {props.socket.send('start a conversation')}}
        >
          Start a conversation
        </button>
      </div>
      <div style={{marginTop: '150px', textAlign: 'center'}}>
        <canvas ref={canvasRef} width={500} height={100}></canvas>
        <div style={{marginTop:'100px'}}>
          <button
            style={{
              width: '100px',
              height: '100px',
              borderRadius: '50%',
              cursor: 'pointer',
              border: 'none',
            }}
            onTouchStart={() => {
              setStatus("recording");
              setMicImage("./mic-32-red.png")
            }}
            onTouchEnd={() => {
              setStatus("inactive")
              setMicImage("./mic-32-black.png")
            }}
            onMouseDown={() => {
              setStatus("recording");
              setMicImage("./mic-32-red.png")
            }}
            onMouseUp={() => {
              setStatus("inactive")
              setMicImage("./mic-32-black.png")
            }}
          >
            <img src={micImage} alt="mic"/>
          </button>
        </div>
        <div style={{display: 'none'}}>
          <AudioAnalyser {...audioProps} />
        </div>
      </div>
    </>
  );
}


export default AudioRecorder;
