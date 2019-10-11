import React from 'react';
import {StyleSheet, Text, TouchableOpacity, View} from 'react-native';
import {DeviceMotion} from 'expo-sensors';



export default class SensorView extends React.Component {
    state = {
        acceleration: {},
        accelerationIncludingGravity: {},
        rotation: {},
        rotationRate: {},
        orientation: null,
    };

    componentDidMount() {
        this._toggle();
    }

    componentWillUnmount() {
        this._unsubscribe();
    }

    _toggle = () => {
        if (this._subscription) {
            this._unsubscribe();
        } else {
            this._subscribe();
        }
    };

    _slow = () => {
        DeviceMotion.setUpdateInterval(100);
    };

    _fast = () => {
        DeviceMotion.setUpdateInterval(16);
    };

    _subscribe = () => {
        this._subscription = DeviceMotion.addListener((
            {acceleration,
            accelerationIncludingGravity,
            rotation,
            rotationRate,
            orientation}
        ) => {
            this.setState({
                acceleration,
                accelerationIncludingGravity,
                rotation,
                rotationRate,
                orientation
            });
        });
    };

    _unsubscribe = () => {
        this._subscription && this._subscription.remove();
        this._subscription = null;
    };

    render() {
        return (
            <View style={styles.sensor}>

                <Text style={styles.textTitle}>acceleration:</Text>
                <Text style={styles.text}>
                    x: {round(this.state.acceleration.x)} y: {round(this.state.acceleration.y)} z: {round(this.state.acceleration.z)}
                </Text>

                <Text style={styles.textTitle}>accelerationIncludingGravity:</Text>
                <Text style={styles.text}>
                    x: {round(this.state.accelerationIncludingGravity.x)}
                    y: {round(this.state.accelerationIncludingGravity.y)}
                    z: {round(this.state.accelerationIncludingGravity.z)}
                </Text>

                <Text style={styles.textTitle}>rotation:</Text>
                <Text style={styles.text}>
                    alpha: {round(this.state.rotation.alpha)}
                    beta:  {round(this.state.rotation.beta)}
                    gamma: {round(this.state.rotation.gamma)}
                </Text>

                <Text style={styles.textTitle}>rotationRate:</Text>
                <Text style={styles.text}>
                    alpha: {round(this.state.rotationRate.alpha)}
                    beta:  {round(this.state.rotationRate.beta)}
                    gamma: {round(this.state.rotationRate.gamma)}
                </Text>

                <Text style={styles.textTitle}>orientation:</Text>
                <Text style={styles.text}>
                    {round(this.state.orientation)}
                </Text>

                <View style={styles.buttonContainer}>
                    <TouchableOpacity onPress={this._toggle} style={styles.button}>
                        <Text>Toggle</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={this._slow} style={[styles.button, styles.middleButton]}>
                        <Text>Slow</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={this._fast} style={styles.button}>
                        <Text>Fast</Text>
                    </TouchableOpacity>
                </View>
            </View>
        );
    }
}

function round(n) {
    if (!n) {
        return 0;
    }

    return Math.floor(n * 100) / 100;
}

const styles = StyleSheet.create({
    buttonContainer: {
        flexDirection: 'row',
        alignItems: 'stretch',
        marginTop: 15,
    },
    button: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#eee',
        padding: 10,
    },
    middleButton: {
        borderLeftWidth: 1,
        borderRightWidth: 1,
        borderColor: '#ccc',
    },
    sensor: {
        marginTop: 45,
        paddingHorizontal: 10,
    },
    text: {
        textAlign: 'center'
    },
    textTitle: {
        textAlign: 'center',
        marginTop: 30
    }
});