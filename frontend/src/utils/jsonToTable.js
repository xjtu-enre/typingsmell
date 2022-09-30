export function jsonToTable(data, infoType, project) {
  var sourceData = [];
  var sourceAxix = [];
  for (var key in data) {
    var value = data[key];
    sourceAxix.push(key);
    sourceData.push(value);
  }
  var option = {
    grid: {
      bottom: 100,
    },
    title: {
      text: project,
    },
    tooltip: {},
    legend: {
      data: [infoType],
    },
    xAxis: {
      data: sourceAxix,
      axisLabel: {
        interval: 0,
        rotate: 40,
      },
    },
    yAxis: {},
    series: [
      {
        name: infoType,
        type: 'bar',
        data: sourceData,
      },
    ],
  };
  return option;
}

export function listToTable(subject, type, data) {
  var sourceSeries = [];
  var seriesType = [];
  var showData = [];
  if (subject === 'commit') {
    showData = data;
  } else {
    for (var info of data) {
      showData.push(info[subject]);
    }
  }
  for (var item in showData[0]) {
    sourceSeries.push(item);
  }
  for (var i = 1; i < sourceSeries.length; i++) {
    seriesType.push({
      type: type,
    });
  }
  var option = {
    grid: {
      bottom: 140,
      right: '20%',
    },
    title: {
      text: subject,
    },
    tooltip: {},
    legend: { type: 'scroll', orient: 'vertical', right: 'right', top: 50 },
    toolbox: {
      show: true,
      feature: {
        magicType: { show: true, type: ['line', 'bar'] },
      },
    },
    dataset: {
      sourceHeader: false,
      dimensions: sourceSeries,
      source: showData,
    },
    dataZoom: [
      {
        show: true,
      },
    ],
    xAxis: {
      type: 'category',
      axisLabel: {
        interval: 0,
        rotate: 40,
      },
    },
    yAxis: {},
    series: seriesType,
  };
  return option;
}

export function toOption(data) {
  var option = [];
  for (var item in data) {
    var children = [];
    for (var file in data[item]) {
      var keyline = '';
      var startLines = []
      for (var line of data[item][file]) {
        keyline += line['start_line'] + '-' + line['end_line'] + ',';
        startLines.push(parseInt(line['start_line']))
      }
      var level2 = { value: { filePath: file, lines: keyline, startLines:startLines }, label: file };
      children.push(level2);
    }
    var level1 = { value: item, label: item, children: children };
    option.push(level1);
  }
  return option;
}

export function selectTimePeriod(timePeriod, data) {
  if (timePeriod == null) {
    return data;
  }
  let filteredData = [];
  let startDate_timestamp = Date.parse(timePeriod[0].replace(/-/g, '/'));
  let endDate_timestamp = Date.parse(timePeriod[1].replace(/-/g, '/'));
  for (let item of data) {
    let oneday = item.date.substr(0, 10);
    let oneday_timestamp = Date.parse(oneday.replace(/-/g, '/'));
    if(oneday_timestamp >= startDate_timestamp && oneday_timestamp <= endDate_timestamp) {
      filteredData.push(item);
    }
  }
  return filteredData;
}