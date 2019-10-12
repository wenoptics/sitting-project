import React from 'react';
import {TouchableHighlight, Modal, StyleSheet, Text, TouchableOpacity, View, TextInput} from 'react-native';
import {DeviceMotion} from 'expo-sensors';


export default class DataSensor extends React.Component {
    state = {
        acceleration: {},
        accelerationIncludingGravity: {},
        rotation: {},
        rotationRate: {},
        orientation: null,

        startTime: Math.floor(Date.now()),
        serverUri: 'ws://172.20.10.3:13254',
        wsConnected: false,
        showDebugView: false,

        modalModeSelectShow: false,
        isSessionStarted: false,

        titleText: ""
    };

    getDebugView(flag) {
        if (flag) {
            return(
                <View style={styles.sensor}>

                    <View
                        style={{
                            borderColor: '#000000',
                            borderWidth: 1,
                            padding: 2,
                            margin: 2,
                        }}>
                        <TextInput
                            numberOfLines={1}
                            // onChangeText={text => onChangeText(text)}
                            value={this.state.serverUri}
                        />
                    </View>

                    <View style={styles.buttonContainer}>
                        <TouchableOpacity onPress={this._btn_connect} style={styles.button}>
                            <Text>Connect ({this.state.wsConnected ? "connected" : "not connected"}) </Text>
                        </TouchableOpacity>
                    </View>

                    <Text style={styles.textTitle}>Time:</Text>
                    <Text style={styles.text}>
                        {Math.floor(Date.now()) - this.state.startTime}
                    </Text>

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
        } else {
            return null
        }
    }

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

            if (this.state.wsConnected) {

                this.ws.send(JSON.stringify({
                    "timestamp": Math.floor(Date.now()) - this.state.startTime,
                    acceleration,
                    accelerationIncludingGravity,
                    rotation,
                    rotationRate,
                    orientation
                }));

            }
        });
    };

    ws = null;

    _unsubscribe = () => {
        this._subscription && this._subscription.remove();
        this._subscription = null;
    };

    startSession = () => {
        if (this.ws !== null && this.state.wsConnected) {
            this.ws.close();
        }
        this.ws = new WebSocket(this.state.serverUri);

        this.ws.onopen = () => {
            // connection opened
            this.ws.send('something'); // send a message
            this.state.wsConnected = true;
            this.state.isSessionStarted = true;
        };

        this.ws.onmessage = (e) => {
            // a message was received
            console.log(e.data);
        };

        this.ws.onerror = (e) => {
            // an error occurred
            console.log(e.message);
        };

        this.ws.onclose = (e) => {
            // connection closed
            console.log(e.code, e.reason);
            this.state.wsConnected = false;
            this.state.isSessionStarted = false;
        };
    };

    endSession() {
        if (this.ws !== null && this.state.wsConnected) {
            this.ws.close();
        }
    }

    _btn_session_startend() {
        if (this.state.isSessionStarted) {
            this.endSession();
            // todo Show Report page
        } else {
            this.state.modalModeSelectShow = true;
        }
    }

    render() {
        return (

            <View style={{
                alignContent: 'center',
                alignItems: 'center',
            }}>

                <View style={styles.buttonContainer}>
                    <TouchableOpacity
                        onPress={()=>{this._btn_session_startend()}}
                        style={styles.bigButton}>
                        <Text style={{fontSize: 20}}>
                            {this.state.isSessionStarted
                                ? 'End Session'
                                : 'Start Now!' } </Text>
                    </TouchableOpacity>
                </View>

                {this.getDebugView(this.state.showDebugView)}

                <Modal
                    animationType="slide"
                    transparent={false}
                    visible={this.state.modalModeSelectShow}>
                    <View style={{
                        marginTop: 100,
                        padding: 50,
                        alignContent: 'center',
                        alignItems: 'center',}}>

                        <Text>
                            Select a mode to get started ...
                        </Text>

                        <View style={styles.buttonContainer}>
                            <TouchableOpacity
                                onPress={()=>{
                                    this.startSession();
                                    this.state.modalModeSelectShow = false;
                                }}
                                style={styles.bigButton}>
                                <Text style={{fontSize: 20}}> Interactive Guide </Text>
                            </TouchableOpacity>
                        </View>

                        <View style={styles.buttonContainer}>
                            <TouchableOpacity
                                onPress={()=>{
                                    this.startSession();
                                    this.state.modalModeSelectShow = false}}
                                style={styles.bigButton}>
                                <Text style={{fontSize: 20}}> Headless Setup </Text>
                            </TouchableOpacity>
                        </View>

                        <View style={{
                            marginTop: 30,
                            alignContent: 'right',
                            alignItems: 'right'}}>
                            <View style={styles.buttonContainer}>
                                <TouchableOpacity
                                    onPress={()=>{this.state.modalModeSelectShow = false}}
                                    style={styles.cancelButton}>
                                    <Text style={{fontSize: 20}}> Cancel </Text>
                                </TouchableOpacity>
                            </View>
                        </View>

                    </View>
                </Modal>

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
    cancelButton: {
        padding: 12,
        textAlign:'center',
        borderWidth: 1,
        borderRadius: 6,
        backgroundColor: 'rgba(238,238,238,0.18)',
        borderColor: 'rgba(99,99,99,0.72)',
    },
    bigButton: {
        padding: 15,
        textAlign:'center',
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 1,
        borderRadius: 6,
        backgroundColor: 'rgba(238,238,238,0.18)',
        borderColor: 'rgba(99,99,99,0.72)',
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