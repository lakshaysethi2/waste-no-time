import React, { useState } from "react";
import MoreLessButton from "./molecules/MoreLessButton";
import Alert from "react-bootstrap/Alert";
import "./inthelast.css";

const PERIOD_LABELS = ["day", "week", "month", "3 mon"];
const DEFAULT_PERIOD_INDEX = 3; // 3 mon view — most representative for alignment

function Number({ tagName, yData, minDur, maxDur }) {
  const which_to_show = DEFAULT_PERIOD_INDEX;
  const [show, setShow] = useState(false);
  const theNumbers = PERIOD_LABELS.map((label, index) => {
    return (
      <div key={index} className="fs-3 p-1 child-row border border-primary">
        <div className="in-the-last">{label}</div>
        {yData[index]}
        <MoreLessButton
          actualDur={yData[index]}
          minDur={minDur}
          maxDur={maxDur}
          tagName={tagName}
        />
      </div>
    );
  });
  const showfalse = () => setShow(false);
  const showTrue = () => setShow(true);
  return (
    <div style={{ paddingRight: "0", paddingLeft: "0" }} className="col-xs-4 col-md-6 col-xl-2">
      <div style={{ minHeight: "200px" }} className="fs-3 fold-children">
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
