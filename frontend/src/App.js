import React from 'react';
import AudioRecorder from "./AudioRecorder.js";


var new_uri;
if (window.location.protocol === "https:") {
    new_uri = "wss:";
} else {
    new_uri = "ws:";
}
new_uri += "//" + window.location.host;
new_uri += window.location.pathname + "api";


window.oncontextmenu = function(event) {
  event.preventDefault();
  event.stopPropagation();
  return false;
};

function App() {
  const [socket] = React.useState(new WebSocket(new_uri))

  return (
    <div class="no_highlights">
      <AudioRecorder socket={socket} />
    </div>
  );
}

export default App;