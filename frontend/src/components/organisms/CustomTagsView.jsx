import React from 'react'
import  tagsArr from '../../variables'
import Number from '../Number'
import getDuration_default from '../../dataController'

function CustomTagsView({tagsArray,data}) {

    tagsArray.forEach((element1, index1) => {
        tagsArr.forEach((element2) => {
            if (element1 === element2[0]) {
                tagsArray[index1] = element2
            }
        })
    })
const customTags = tagsArray.map((element, index) => {
    let [tag,min,max] = element
      return (
        <Number
          key={index.toString()}
          minDur={min}
          maxDur={max}
          yData={getDuration_default(tag,data)}
          tagName={tag}
        />
      );
  });
  return (
    <>
      {customTags}
    </>
  )
}

export default CustomTagsView
