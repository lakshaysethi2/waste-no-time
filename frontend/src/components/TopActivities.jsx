import React from "react";
import MoreLessButton from "./molecules/MoreLessButton";

function TopActivities({ data }) {
  return (
    <div>
      <div className="row border">
        {data.map((elem, index) => {
          return (
            <div key={index} className="col-md-4 col-xl-2 col-xs-12">
      
                <div className="border">in the last {elem[0]} hours</div>
                <br />
                {elem[1].map((elem, index) => (
                  <div style={{minHeight:"50px"}} className="border" key={index}>
                    <MoreLessButton
                      actualDur={elem[1]}
                      minDur={elem[2]}
                      maxDur={elem[3]}
                      tagName={elem[0]}
                      showMinMax={true}
                    />
                  </div>
                ))}
              </div>
           
          );
        })}
      </div>
    </div>
  );
}

export default TopActivities;
