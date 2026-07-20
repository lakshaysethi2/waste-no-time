import React from 'react';
import Button from 'react-bootstrap/Button';

function LastUpdated({time,setBgColor}) {
  const stickyStyle = {
    position: "sticky",
    top: 0,
    textAlign:"end",
    zIndex:3
  }
  return (
    <div style={stickyStyle}>
        <div style={{fontSize:"1vh"}}>
            Last Updated at {time}
        </div>
        <Button style={{fontSize:"1vh"}} size="sm" onClick={()=>setBgColor("white")} variant="light">Light</Button>
        <Button style={{fontSize:"1vh"}} size="sm" onClick={()=>setBgColor("black")} variant="dark">dark</Button>
    </div>
  )
}

export default LastUpdated