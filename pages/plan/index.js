// Line.js
// wxChart 线形图
let app = getApp()

let WxChart = require('../../utils/wxcharts.js');
let Utils = require("../../utils/util.js");

const labels = ['1号', '2号', '3号', '4号', '5号', '6号', '7号'];

// Base line chart
let baseLine = windowWidth => {
    let wxLiner = new WxChart.WxLiner('baseLine', {
        width: windowWidth,
        height: 250,
        title: '计划燃尽图',
        yScaleOptions: {
            position: 'left',
            title: '元'
        },
        legends: [{
            text: '巧克力'
        }]
    });

    wxLiner.update(Utils.dataGenerator(labels));
    return {
        chart: wxLiner,
        redraw: () => {
            wxLiner.update(Utils.dataGenerator(labels));
        }
    };
};

let multiLine = windowWidth => {
    let wxLiner = new WxChart.WxLiner('multiLine', {
        width: windowWidth,
        height: 250,
        title: '计划燃尽图',
        yScaleOptions: {
            position: 'left',
            title: '剩余金钱(元)'
        },
        legends: [{
            text: '预期花费',
            key: 'chocolate'
        }, {
            text: '实际花费',
            key: 'fruit'
        }],
        tooltip: {
          model: 'axis'
        }
    });

    wxLiner.update(Utils.dataGenerator(labels, ['chocolate', 'fruit']));
    return {
        chart: wxLiner,
        redraw: () => {
            wxLiner.update(Utils.dataGenerator(labels, ['chocolate', 'fruit']));
        }
    };
};

let multiFillLine = windowWidth => {
    let wxLiner = new WxChart.WxLiner('multiFillLine', {
        width: windowWidth,
        height: 250,
        title: '销售额',
        yScaleOptions: {
            position: 'left',
            title: '元'
        },
        crossScaleOptions: {
            xFirstPointSpace: 0
        },
        legends: [{
            text: '日用品',
            key: 'dailyNecessities',
            fillArea: true,
            fillStyle: '#3385ff',
            strokeStyle: '#3385ff'
        }, {
            text: '水果',
            key: 'fruit',
            fillArea: true,
            fillStyle: '#238456',
            strokeStyle: '#238456'
        }, {
            text: '家电',
            key: 'appliances'
        }],
        tooltip: {
          model: 'axis'
        }
    });

    wxLiner.update(Utils.dataGenerator(labels, ['dailyNecessities', 'fruit', 'appliances']));
    return {
        chart: wxLiner,
        redraw: () => {
            wxLiner.update(Utils.dataGenerator(labels, ['dailyNecessities', 'fruit', 'appliances']));
        }
    };
};



Page({
    /**
     * 页面的初始数据
     */
    data: {},

    changeChart: function (e) {
        let canvasName = e.target.dataset.canvasName;
        let chart = this[canvasName + 'Chart'];
        chart.redraw();
    },

    /**
     * 生命周期函数--监听页面初次渲染完成
     */
    onReady: function () {
        let me = this;
        let windowWidth = 320;
        try {
            let res = wx.getSystemInfoSync();
            windowWidth = res.windowWidth;
        } catch (e) {
            // do something when get system info failed
        }

        me.baseLineChart = baseLine(windowWidth);
        me.multiLineChart = multiLine(windowWidth);
        me.multiFillLineChart = multiFillLine(windowWidth);

        me.baseLineChart.chart.once('draw', function (views) {
          me.baseLineChartTapHandler = this.mouseoverTooltip(views);
        }, me.baseLineChart.chart);

        me.multiLineChart.chart.once('draw', function (views) {
          me.multiLineChartTapHandler = this.mouseoverTooltip(views);
        }, me.multiLineChart.chart);

        me.multiFillLineChart.chart.once('draw', function (views) {
          me.multiFillLineChartTapHandler = this.mouseoverTooltip(views);
        }, me.multiFillLineChart.chart);
    }
});