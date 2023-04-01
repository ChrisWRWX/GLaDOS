import React from 'react';
import AudioRecorder from "./AudioRecorder.js";

function App() {

  const [socket] = React.useState(new WebSocket('ws://localhost:8001'))

  return (
    <div>
      <AudioRecorder socket={socket} />
    </div>
  );
}

export default App;