import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: surfaceColor
    height: 40
    radius: 8

    property string message: ""
    property string type: "info"  // info, error, success
    property real progress: 0

    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        Text {
            text: message
            color: {
                switch(type) {
                    case "error": return "#ff5252"
                    case "success": return "#4caf50"
                    default: return textColor
                }
            }
            Layout.fillWidth: true
        }

        ProgressBar {
            visible: progress > 0 && progress < 100
            value: progress / 100
            Layout.preferredWidth: 100
        }
    }
} 