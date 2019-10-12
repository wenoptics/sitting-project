import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import DataSensor from './components/DataSensor'
import ThreeView from './components/ThreeView'

export default function App() {

    return (
        <View style={styles.container}>
            <DataSensor/>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
        alignItems: 'center',
        justifyContent: 'center',
    },
});

