import React from "react";
import "./flash.css"
function MoreLessButton(props) {
  const { onClick, actualDur, minDur, maxDur, tagName,showMinMax } = props;
  let color = "bg-warning";
  actualDur <= minDur && minDur !== 0
    ? (color = "bg-warning")
    : actualDur >= maxDur && maxDur !== 0
    ? (color = "bg-danger")
    : maxDur === undefined
    ? (color = "bg-warning")
    : (color = "bg-success");

  return (
    <div
      onClick={onClick}
      style={{ minHeight: "inherit" }}
      className={`${color} position-relative`}
    >
    { (color.includes("danger")|| color.includes("warning") ) && <div style={{
        animation: "flash 0.5s linear infinite",
      }}
    > WARNING</div>}
      <div className="position-absolute top-50 start-50 translate-middle">
        {actualDur} - {tagName}
      </div>
      {showMinMax && <div style={{fontSize:"10px"}}>{minDur} to {maxDur} </div>}
    </div>
  );
}

export default MoreLessButton;
