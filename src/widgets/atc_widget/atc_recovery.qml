import QtQuick 2.7
import QtQuick.Controls 1.5
import QtQuick.Layouts 1.3

Rectangle {
    id: root
    width: 400
    height: 600
    color: atc_recovery.backgroundColor
    border.color: "gray"
    border.width: 2

    property string recovery_status: "Ready"
    property string current_step: ""
    property int recovery_progress: 0

    Text {
        id: title
        text: "ATC Recovery Wizard"
        font.pixelSize: 18
        font.bold: true
        color: "white"
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 20
    }

    Rectangle {
        id: status_panel
        width: parent.width - 40
        height: 100
        anchors.top: title.bottom
        anchors.topMargin: 20
        anchors.horizontalCenter: parent.horizontalCenter
        color: "black"
        border.color: "gray"
        border.width: 1

        Column {
            anchors.centerIn: parent
            spacing: 10

            Text {
                id: status_text
                text: "Status: " + recovery_status
                color: "white"
                font.pixelSize: 14
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                id: step_text
                text: current_step
                color: "lightblue"
                font.pixelSize: 12
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Rectangle {
                id: progress_bar_bg
                width: 300
                height: 20
                color: "darkgray"
                border.color: "gray"
                border.width: 1
                anchors.horizontalCenter: parent.horizontalCenter

                Rectangle {
                    id: progress_bar
                    height: parent.height - 2
                    width: parent.width * (recovery_progress / 100)
                    y: 1
                    x: 1
                    color: "lightgreen"
                }
            }
        }
    }

    GridLayout {
        id: button_grid
        columns: 2
        anchors.top: status_panel.bottom
        anchors.topMargin: 30
        anchors.horizontalCenter: parent.horizontalCenter
        columnSpacing: 20
        rowSpacing: 15

        Button {
            text: "Resume\nMid-Change"
            width: 120
            height: 60
            enabled: true
            onClicked: atc_recovery.resume_mid_change()
        }

        Button {
            text: "Home ATC"
            width: 120
            height: 60
            enabled: true
            onClicked: atc_recovery.home_atc()
        }

        Button {
            text: "Clear Fault"
            width: 120
            height: 60
            enabled: true
            onClicked: atc_recovery.clear_fault()
        }

        Button {
            text: "Complete\nRecovery"
            width: 120
            height: 60
            enabled: recovery_progress >= 100
            onClicked: atc_recovery.complete_recovery()
        }
    }

    Text {
        text: "Manual Jog to Pocket:"
        color: "white"
        font.pixelSize: 14
        anchors.top: button_grid.bottom
        anchors.topMargin: 30
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Row {
        id: pocket_buttons
        anchors.top: button_grid.bottom
        anchors.topMargin: 60
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 10

        Repeater {
            model: 12
            Button {
                text: (index + 1).toString()
                width: 30
                height: 30
                onClicked: atc_recovery.manual_jog_to_pocket(index + 1)
            }
        }
    }

    Text {
        text: "Recovery Actions:"
        color: "white"
        font.pixelSize: 14
        anchors.top: pocket_buttons.bottom
        anchors.topMargin: 30
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Column {
        anchors.top: pocket_buttons.bottom
        anchors.topMargin: 60
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 10

        Text {
            text: "• Resume Mid-Change: Continue interrupted tool change"
            color: "white"
            font.pixelSize: 10
            width: 350
            wrapMode: Text.WordWrap
        }

        Text {
            text: "• Home ATC: Return carousel to home position"
            color: "white"
            font.pixelSize: 10
            width: 350
            wrapMode: Text.WordWrap
        }

        Text {
            text: "• Clear Fault: Reset ATC fault state to Ready"
            color: "white"
            font.pixelSize: 10
            width: 350
            wrapMode: Text.WordWrap
        }

        Text {
            text: "• Manual Jog: Move carousel to specific pocket"
            color: "white"
            font.pixelSize: 10
            width: 350
            wrapMode: Text.WordWrap
        }
    }

    Connections {
        target: atc_recovery

        function onRecoveryStatusSig(status) {
            recovery_status = status;
        }

        function onRecoveryStepSig(step) {
            current_step = step;
        }

        function onRecoveryProgressSig(progress) {
            recovery_progress = progress;
        }
    }
}