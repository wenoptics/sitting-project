import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import SensorView from './components/SensorView'

export default function App() {
  return (
    <View style={styles.container}>
      <SensorView/>
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
