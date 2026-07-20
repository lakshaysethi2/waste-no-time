import React, { useState } from "react";
import MoreLessButton from "./molecules/MoreLessButton";
import Alert from "react-bootstrap/Alert";
import "./inthelast.css"

function Number({ tagName, yData, minDur, maxDur }) {
  const which_to_show= 3// 0, 1,2,3 day week, month, 3mon
  const [show, setShow] = useState(false);
  const theNumbers = [0, 1, 2, 3].map((element, index) => {
    return (
      <div key={index} className="fs-3 p-1 child-row border border-primary">
        <div className="in-the-last">{index===0 ? "day" : index===1 ? "week"  : index===2 ? "month" : "3 mon"}</div>
        {yData[element]}
        <MoreLessButton
          actualDur={yData[element]}
          minDur={minDur}
          maxDur={maxDur}
          tagName={tagName}
        />
      </div>
    );
  });
  const showfalse = () => {setShow(false)}
  const showTrue = () =>{ setShow(true)}
  return (
    <div style={{paddingRight:"0",paddingLeft:"0"}} 
      className="col-xs-4 col-md-6 col-xl-2"
    >
        <div style={{minHeight:"200px"}} className="fs-3 fold-children">
          <Alert show={show} variant="success">
            {minDur} - {maxDur}
            {theNumbers}
            <div className="d-flex justify-content-end">
                <MoreLessButton
                  onClick={showfalse}
                  actualDur={yData[which_to_show]}
                  minDur={minDur}
                  maxDur={maxDur}
                  tagName={tagName}
                />
            </div>
          </Alert>

          {!show && (
              <MoreLessButton
                onClick={showTrue}
                actualDur={yData[which_to_show]}
                minDur={minDur}
                maxDur={maxDur}
                tagName={tagName}
              />
          )}
        </div>
    </div>
  );
}

export default Number;
