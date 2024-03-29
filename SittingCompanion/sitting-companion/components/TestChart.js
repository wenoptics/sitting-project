import React, {
    Component
} from 'react';
import {
    Platform,
    StyleSheet,
    Text,
    View,
} from 'react-native';
import WebView from 'react-native-webview'

import Chart from 'react-native-chartjs';
const chartConfiguration = {
    type: 'bar',
    data: {
        labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
        datasets: [{
            label: '# of Votes',
            data: [12, 19, 3, 5, 2, 3],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255,99,132,1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        maintainAspectRatio : false,
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    }

};

export default class TestChartView extends Component {
    constructor(props) {
        super(props);

        this.state = {
            chartConfiguration : chartConfiguration
        };
    }
    render() {

        return (
            <View style = {{ flex : 1 }}>
                <WebView
                    source={{
                        uri: 'http://172.20.10.3:8000/ReportApp/OverallReport.html'
                        // uri: 'https://www.chartjs.org/samples/latest/charts/area/line-boundaries.html'
                        // html:{HTML_REPORT}
                    }}
                    style={{marginTop: 20}}
                />
            </View>
        );
    }
}

const HTML_REPORT ='';