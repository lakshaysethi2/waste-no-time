import "./App.css";
import axios from "axios";
import { BrowserRouter as Router, Route,Routes } from 'react-router-dom';
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

function transformData(responseData) {
  // Django returns a flat array of activities; wrap in {activities: [...]}
  if (Array.isArray(responseData)) {
    return { activities: responseData };
  }
  return responseData;
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

const get_total_hours_today = () =>{
  const d = new Date();
  return d.getHours();
}

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
  return (
    <div >
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

    </div>
  );
}

function App() {
  const [userLoggedIn,setUserLoggedIn] = useState(false)
  const [, setAuthData] = useState({})
  const [jsonData,setJSONData] = useState({"activities":[]})
  const [information,setInformation] = useState("started")
  const [lastDataFetched, setLastDataFetched] = useState(`${(new Date()).getHours()}:${(new Date()).getMinutes()}`)
  
  const getData = () => {
    setInformation(<><br/><br/><Spinner animation="border" /> {"Loading..."}</>)
    axios("/api/activities")
    .then((result)=>{
        const transformed = transformData(result.data);
        setJSONData(transformed)
        if (transformed.activities.length > 0) {
          setLastDataFetched(`${(new Date()).getHours()}:${(new Date()).getMinutes()}`)
          setInformation("")
        }
    })
  }

  useEffect(() => {
    if (!userLoggedIn) return undefined;
    getData();
    const intervalId = window.setInterval(getData, 1000 * 60 * 60);
    return () => window.clearInterval(intervalId);
  }, [userLoggedIn]);
  const sideBySide = (arr,jsonData) => {
    return (
      <div className="row">
        <div className="col-8">
          <TopActivities data={getTopActData(arr,jsonData) }/>
        </div>
        <div className="col-4">
          {idealtop}
        </div>
      </div>
    )
  }

  const theLogin = <Login setUserLoggedIn={setUserLoggedIn} setAuthData={setAuthData}/>

  return (
    <>
    <div  className="App">
    <h1>Metrics: you reap what you sow</h1>
    <Router>
      <Navigation userLoggedIn={userLoggedIn} getData={getData}/>
    <div>{information}</div>
    <LastUpdated time={lastDataFetched} />
    <br/>
      <Routes>
      <Route exact path="/" element={!userLoggedIn ? theLogin : <Home data={jsonData}/> } />
      <Route exact path="/going" element={!userLoggedIn ? theLogin : <PowerBI data={jsonData}/>  } />
      <Route path="/top" element={!userLoggedIn ? theLogin :<>not implemented</> } />
      <Route path="/today" element={!userLoggedIn ? theLogin :sideBySide([24*90,get_total_hours_today()],jsonData) } />
      <Route path="/top/24" element={!userLoggedIn ? theLogin :sideBySide([24*90,24],jsonData) } />
      <Route path="/top/12" element={!userLoggedIn ? theLogin :sideBySide([24*90,12],jsonData) } />
      <Route path="/top/48" element={!userLoggedIn ? theLogin :sideBySide([24*90,24*2],jsonData) } />
      <Route path="/top/72" element={!userLoggedIn ? theLogin :sideBySide([24*90,24*3],jsonData) } />
      <Route path="/top/120" element={!userLoggedIn ? theLogin :sideBySide([24*90,24*5],jsonData) } />
      <Route path="/top/168" element={!userLoggedIn ? theLogin :sideBySide([24*90,24*7],jsonData) } />
      <Route path="/top/336" element={!userLoggedIn ? theLogin :sideBySide([24*90,24*14],jsonData) } />
      <Route path="/top/720" element={!userLoggedIn ? theLogin :sideBySide([24*90,24*30],jsonData) } />
      <Route path="/top/2160" element={topActs([2160],jsonData)} />
      {<Route path="/login" element={theLogin} /> }
      {<Route path="/RLNS" element={<CustomTagsView data={jsonData}  tagsArray={['ss','reading',"writing"]} />} /> }
      {<Route path="/WRK" element={<CustomTagsView data={jsonData} tagsArray={['job','programming',"writing", "linux"]} />} /> }
      {<Route path="/RMB" element={<CustomTagsView data={jsonData} tagsArray={['goal setting',"writing",'money','reading','job apply','udemy', "programming", "linux"]} />} /> }
      {<Route path="/HLTH" element={<CustomTagsView data={jsonData} tagsArray={['exercise','sleep','food',"bio"]} />} /> }

      </Routes>
    </Router>
    </div>
    </>
  )


}

export default App;
