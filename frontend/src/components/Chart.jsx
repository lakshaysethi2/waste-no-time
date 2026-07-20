import React from 'react'

function Chart({tagName,xData,yData}) {
  const theBars = yData.map((element,index) => {
    return (
        <div key={index} style={{height:`${element*300}px`}}  className='d-inline-block a_bar' >
            {element} 
        </div>
    )
  })
  return (
    <div className="col-sm-12">
        <div className='chart_container'>
            <h5>{tagName} chart</h5>

            <div className="chart_box d-flex">
                {theBars}
            </div>
            <div className="justify x_axis">
                {xData.map((element,index) => <div key={index} className='d-inline' > {element} </div>)}
            </div>

        </div>            

    </div>
  )
}

export default Chart