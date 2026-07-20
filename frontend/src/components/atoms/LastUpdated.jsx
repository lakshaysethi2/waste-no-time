import React from 'react';

function LastUpdated({time}) {
  const stickyStyle = {
    position: "sticky",
    top: 0,
    textAlign:"end",
    zIndex:3
  }
  return (
    <div style={stickyStyle}>
        <div style={{fontSize:"2vh"}}>
            Last Updated at {time}
        </div>
    </div>
  )
}

export default LastUpdated