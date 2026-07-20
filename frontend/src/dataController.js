import {tagsArr} from './App'
const millisec_in_one_hour = 1000 * 60 * 60;
const millisec_in_one_day = 24 * millisec_in_one_hour
const NUMBER_OF_HOURS_BACK = 1
const NUMBER_OF_DURPAIRS_TO_DISPLAY=10
function realityExpectationGap(a) {
  // idealy try to give a positive number
  let reality = a.props.yData[2];
  let gap = 0;
  let expectation = 0;
  if (a.props.maxDur === 0) {
    expectation = a.props.minDur;
    gap = expectation - reality;
  } else {
    expectation = a.props.maxDur;
    gap = reality - expectation;
  }
  return gap
}

function getDuration_default(tagName, data) {
  let now = Date.now();
  let month =
    Math.round(
      (get_tag_duration(tagName, now, now - 24 * 30 * millisec_in_one_hour,data) /
        30) *
        100
    ) / 100;
  let last_week =
    Math.round(
      (get_tag_duration(tagName, now, now - 24 * 7 * millisec_in_one_hour,data) /
        7) *
        100
    ) / 100;
  let last_day = get_tag_duration(tagName, now, now - 20 * millisec_in_one_hour,data);
  let three_month =
    Math.round(
      (get_tag_duration(tagName, now, now - 24 * 90 * millisec_in_one_hour,data) /
        90) *
        100
    ) / 100;
  return [last_day, last_week, month, three_month];
}

function get_tag_duration(tag_name, totime, fromtime, data) {
  if (tag_name.indexOf("_") > -1) {
    tag_name = tag_name.replace("_", " ");
  }
  //get all activities in from to
  console.assert (data !== undefined, "data is undefined in get_tag_duration")
  let all_acts = get_all_acts(fromtime, totime,data);
  // filter all activities to exer
  let tag_acts = [];
  for (const elem of all_acts) {
    if (elem.displayName.toLowerCase() === tag_name.toLowerCase()) {
      tag_acts.push(elem);
    }
  }
  if (tag_acts.length === 0) {
    return 0;
  } else {
    //calc total time deltas
    let total_dur = 0;
    for (const elem of tag_acts) {
      total_dur +=
        new Date(elem.endTime).valueOf() - new Date(elem.startTime).valueOf();
    }
    // convert the toal time into hours
    let total_dur_in_hours =
      Math.round((total_dur / 1000 / 60 / 60) * 100) / 100;
    return total_dur_in_hours;
  }
}

function get_all_acts(fromtime, totime,data) {
  console.assert (data !== undefined, "data is undefined")
  let all_acts = [];
  for (const elem of data.activities) {
    let act_st = new Date(elem.startTime);
    let act_et = new Date(elem.endTime);
    let the_totime = new Date(totime);
    let the_fromtime = new Date(fromtime);
    let act_started_after_the_st = act_st.valueOf() > the_fromtime.valueOf();
    let act_ended_before_the_endtime = act_et.valueOf() < the_totime.valueOf();
    if (act_started_after_the_st) {
      if (act_ended_before_the_endtime) {
        all_acts.push(elem);
      }
    }
  }
  return all_acts;
}


function getTopActData(the_from_times, data) {
  if (the_from_times[0] === 0){
    let the_time_now = new Date()
    let hours_since_midnight = the_time_now.getHours() +NUMBER_OF_HOURS_BACK
    the_from_times.unshift(hours_since_midnight)
  }
  let main_arr = [];
  for (const hours of the_from_times) {
    let now = Date.now().valueOf();
    let from_time = now - hours * millisec_in_one_hour;
    console.assert(data !== undefined, "data is undefined")
    let all_acts = get_all_acts(from_time, now,data);
    let all_unique_acts = get_unique_act_names(all_acts);
    let all_act_dur_pairs = [];
    for (const act_name of all_unique_acts) {
      let act_dur_pair = [];
      act_dur_pair.push(act_name);     
      if (hours<24){
        act_dur_pair.push(Math.round(get_tag_duration(act_name, now, from_time,data)* 100) / 100)
      }else{
        act_dur_pair.push(Math.round(get_tag_duration(act_name, now, from_time,data)/(hours/24) * 100) / 100)
      }
      let minDur = getMinDur(act_name)
      let maxDur = getMaxDur(act_name)
      act_dur_pair.push(minDur)
      act_dur_pair.push(maxDur)
      all_act_dur_pairs.push(act_dur_pair);
    }
    let sorted_dur_pairs = all_act_dur_pairs.sort(compareFn);
    let top_acts = sorted_dur_pairs.slice(0, NUMBER_OF_DURPAIRS_TO_DISPLAY);
    let delta_and_top_acts = [hours, top_acts];
    main_arr.push(delta_and_top_acts);
  }
  return main_arr;
}

function get_unique_act_names(acts_arr) {
  let names_only_arr = [];
  for (const act of acts_arr) {
    names_only_arr.push(act.displayName);
  }
  return [...new Set(names_only_arr)];
}

function compareFn(a, b) {
  if (a[1] > b[1]) {
    return -1;
  }
  if (a[1] < b[1]) {
    return 1;
  }
  return 0;
}

function getMinDur(act_name){
  for (const act of tagsArr){
    if (act[0].toLowerCase() === act_name.toLowerCase()){
      return act[1]
    }
  }
}
function getMaxDur(act_name){
  for (const act of tagsArr){
    if (act[0].toLowerCase() === act_name.toLowerCase()){
      return act[2]
    }
  }
}


function getIdealTopActData() {
  let main_arr = [];
  main_arr.push(["ideal 24",[
    ['sleep',7,6.5,7.5],
    ['programming',3,1,0],
    ['udemy',1.1,1,0],
    ['job',2,1,0],
    ['linux',2,1,0],
    ['gamming',2,1,0],
    ['exercise',.51,.49,0],
    ['reading',1.1,1,0],
    ['writing',1.1,1,0],
    ['ecl',1,0.01,1.2],
  ]])
  return main_arr;
}

function get_total_hours_last_x_day(tag_name,x,data) {
  let now = Date.now().valueOf()
  let from_time = now - (x+1) * millisec_in_one_day
  let to_time = now - x * millisec_in_one_day
  let total_dur = get_tag_duration(tag_name, to_time, from_time,data)
  let total_dur_in_hours = Math.round(total_dur * 100) / 100
  return total_dur_in_hours
}


function trendDataGenerator(data,list_of_tags) {
  if( data.activities.length === 0){
    return []
  }
  let chart_data = [
    ['now-xDays', ...list_of_tags],
  ];
  for (let i = 0; i < 14; i++) {
    let row = [i]
    for (let j = 0; j < list_of_tags.length; j++) {
      row.push(get_total_hours_last_x_day(list_of_tags[j],i,data))
    }
    chart_data.push(row)
  }
  
  return  chart_data

}

export default getDuration_default;
export {
  getTopActData,
  getIdealTopActData,
  realityExpectationGap,
  trendDataGenerator,
  get_unique_act_names,
  };
