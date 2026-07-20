import React, {useState} from 'react'
import { Chart } from "react-google-charts";
// import {get_unique_act_names,trendDataGenerator} from '../../dataController'
import {trendDataGenerator} from '../../dataController'
import "./chart.css"

function PowerBI({data}) {
  // const list_of_tags = get_unique_act_names(data.activities);
  const list_of_tags = [
    "sick",
    "food",
    "Driving",
    "Other people",
    "sleep",
    "ecl",
    ]

  const [chart_data,setChartData] = useState(trendDataGenerator(data,list_of_tags))

  return (
    <div>
      <Chart
        chartType="LineChart"
        title='recent trends'
        curveType='function'
        data={chart_data}
        width="100%"
        height="400px"
        legendToggle
      />
      { list_of_tags.map((tag_name,index) => {
          return (
            <div className='chart_btn' onClick={()=>{
              setChartData(trendDataGenerator(data,[tag_name]))
            }} 
              key={index.toString()}>
                 {tag_name} 
            </div>
            )
          })
        }
    </div>
  )
}
export default PowerBI
