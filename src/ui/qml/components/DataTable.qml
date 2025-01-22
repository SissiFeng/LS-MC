import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: surfaceColor
    radius: 8

    property var tableModel: []
    property var columnHeaders: []

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 10

        // Table header
        Rectangle {
            Layout.fillWidth: true
            height: 40
            color: Qt.rgba(1, 1, 1, 0.1)
            radius: 4

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Repeater {
                    model: columnHeaders
                    Text {
                        text: modelData
                        color: textColor
                        font.pixelSize: 14
                        font.weight: Font.Medium
                        Layout.fillWidth: true
                    }
                }
            }
        }

        // Table content
        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: tableModel

            delegate: Rectangle {
                width: parent.width
                height: 40
                color: index % 2 === 0 ? "transparent" : Qt.rgba(1, 1, 1, 0.05)

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10

                    Repeater {
                        model: columnHeaders
                        Text {
                            text: modelData in rowData ? rowData[modelData] : ""
                            color: textColor
                            Layout.fillWidth: true
                        }
                    }
                }
            }
        }
    }
} 