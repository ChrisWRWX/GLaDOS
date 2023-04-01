import React from 'react';
import AudioRecorder from "./AudioRecorder.js";


const loc = window.location;
var new_uri;
if (window.location.protocol === "https:") {
    new_uri = "wss:";
} else {
    new_uri = "ws:";
}
new_uri += "//" + window.location.host;
new_uri += window.location.pathname + "api";



function App() {
  const [socket] = React.useState(new WebSocket(new_uri))

  return (
    <div>
      <AudioRecorder socket={socket} />
    </div>
  );
}

export default App;