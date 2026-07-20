import "./App.css";
import axios from "axios";
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import "bootstrap/dist/css/bootstrap.min.css";
import Number from "./components/Number";
import Login from "./components/molecules/Login";
import PowerBI from "./components/organisms/PowerBI";
import Navigation from "./components/molecules/Navigation";
import CustomTagsView from "./components/organisms/CustomTagsView";
import getDuration_default, {
  getTopActData,
  getIdealTopActData,
  realityExpectationGap,
} from "./dataController";
import TopActivities from "./components/TopActivities";
import LastUpdated from "./components/atoms/LastUpdated";
import React, { useState,useEffect } from 'react';

import tagsArr from './variables'
import Spinner from 'react-bootstrap/Spinner';

// Transform Django flat array to dashboard expected shape
function transformData(rawData) {
  if (!Array.isArray(rawData)) {
    return { activities: [] };
  }
  return {
    activities: rawData.map(item => ({
      ...item,
      displayName: item.name,
      startTime: item.start_time,
      endTime: item.end_time,
    }))
  };
}


function compareFn(a, b) {
  if (realityExpectationGap(a) >= realityExpectationGap(b)) {
    return -1;
  } else {
    return 1;
  }
}


const idealtopActsData = getIdealTopActData();


const topActs = (hours,data) =>  <TopActivities data={getTopActData(hours,data)} />;


const idealtop = <TopActivities data={idealtopActsData} />;

function Home ({data}){
  const numbersPrevent = tagsArr.map((element, index) => {
    let [tag,min,max] = element
    if (max !== 0) {
      return (
        <Number
          key={index.toString()}
          minDur={min}
          maxDur={max}
          yData={getDuration_default(tag,data)}
          tagName={tag}
        />
      );
    }
  });
  const numbersPromote = tagsArr.map((element, index) => {
    let [tag,min,max] = element
    if (max === 0) {
      return (
        <Number
          key={index.toString()}
          minDur={min}
          maxDur={max}
          yData={getDuration_default(tag,data)}
          tagName={tag}
        />
      );
    }
  });
  
  const sortedNumbersPromote = numbersPromote.sort(compareFn);
  const sortedNumbersPrevent = numbersPrevent.sort(compareFn);
  const topActivities = <TopActivities data={getTopActData([0,1,24, 48, 24 * 7, 24 * 30, 24 * 90],data)} />;
  const [bgColor, setBgColor] = useState("white");
  return (
    <div style={{backgroundColor:bgColor}} className="App">
      <LastUpdated setBgColor={setBgColor} time={`${(new Date()).getHours()}:${(new Date()).getMinutes()}`} />
      <div className="row">
        <div className="col-12 border border-info">
          <div className="row">
            <div>promote:</div>
            {sortedNumbersPromote}
          </div>
        </div>

        <div className="col-12 border border-danger">
          <div className="row">
            {sortedNumbersPrevent}
          </div>
        </div>

        {topActivities}
        {idealtop}
      </div>
      <PowerBI />
    </div>
  );
}

function App() {
  const [userLoggedIn,setUserLoggedIn] = useState(false)
  const [jsonData,setJSONData] = useState({"activities":[]})
  const [information,setInformation] = useState("started")
  const getData = () => {
    setInformation(<><br/><br/><Spinner animation="border" /> {"Loading..."}</>)
    axios("/api/activities?chat_id=1040271347")
    .then((result)=>{
        const transformed = transformData(result.data);
        setJSONData(transformed)
        if (transformed.activities.length > 0) {
          setInformation("")
        }
    })
  }

  useEffect(()=>{
    getData()
  },[])

  const theLogin = <Login setUserLoggedIn={setUserLoggedIn}/>
  return (
    <>
    <h1>Metrics: you reap what you sow</h1>
    <Router>
      <Navigation userLoggedIn={userLoggedIn} getData={getData}/>
    <div>{information}</div>
    <br/>
      <Routes>
      <Route exact path="/" element={userLoggedIn ? <Home data={jsonData}/> :  topActs([2160],jsonData) } />
      <Route exact path="/going" element={userLoggedIn ? <PowerBI data={jsonData}/> :  topActs([2160],jsonData) } />
      <Route path="/top" element={!userLoggedIn ? theLogin :<>not implemented</> } />
      <Route path="/top/24" element={!userLoggedIn ? theLogin : topActs([24],jsonData)} />
      <Route path="/top/48" element={!userLoggedIn ? theLogin : topActs([48],jsonData)} />
      <Route path="/top/72" element={!userLoggedIn ? theLogin : topActs([72],jsonData)} />
      <Route path="/top/120" element={!userLoggedIn ? theLogin : topActs([120],jsonData)} />
      <Route path="/top/168" element={!userLoggedIn ? theLogin : topActs([168],jsonData)} />
      <Route path="/top/336" element={!userLoggedIn ? theLogin : topActs([336],jsonData)} />
      <Route path="/top/720" element={!userLoggedIn ? theLogin : topActs([720],jsonData)} />
      <Route path="/top/2160" element={topActs([2160],jsonData)} />
      {<Route path="/login" element={userLoggedIn ? <Navigate to="/" /> : theLogin} /> }
      {<Route path="/RLNS" element={<CustomTagsView data={jsonData}  tagsArray={['ss','reading',"writing"]} />} /> }
      {<Route path="/WRK" element={<CustomTagsView data={jsonData} tagsArray={['job','programming',"writing", "linux"]} />} /> }
      {<Route path="/RMB" element={<CustomTagsView data={jsonData} tagsArray={['goal setting',"writing",'money','reading','job apply','udemy', "programming", "linux"]} />} /> }
      {<Route path="/HLTH" element={<CustomTagsView data={jsonData} tagsArray={['exercise','sleep','food',"bio"]} />} /> }

        {/* { sortedNumbersPromote.map((number,index)=>{
          if (number!==undefined){
            return <Route path={number.props.tagName} key={index} element={!userLoggedIn ? theLogin :number} />
          }
        
        })} */}

      </Routes>
    </Router>
    </>
  )


}

export default App;
export { tagsArr };
