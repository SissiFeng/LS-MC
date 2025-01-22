import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "./components"

ApplicationWindow {
    id: window
    width: 1200
    height: 800
    visible: true
    title: "Waters Data Converter"

    // Modern dark theme colors
    property color primaryColor: "#2196F3"
    property color backgroundColor: "#121212"
    property color surfaceColor: "#1E1E1E"
    property color textColor: "#FFFFFF"

    color: backgroundColor

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        // Header
        Rectangle {
            Layout.fillWidth: true
            height: 60
            color: surfaceColor
            radius: 8

            Text {
                anchors.centerIn: parent
                text: "Waters Data Converter"
                color: textColor
                font.pixelSize: 24
                font.weight: Font.Medium
            }
        }

        // Main content
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 20

            // Left panel
            ColumnLayout {
                Layout.preferredWidth: 300
                Layout.fillHeight: true
                spacing: 20

                FileUploader {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 200
                    onFilesSelected: backend.processFiles(files)
                }

                ParameterConfig {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    onParametersChanged: backend.updateParameters(params)
                }
            }

            // Right panel
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 20

                DataTable {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    tableModel: backend.resultData
                    columnHeaders: ["retention_time", "intensity", "area", "width"]
                }

                // Export button
                Button {
                    text: "导出结果"
                    onClicked: backend.exportResults()
                }

                StatusBar {
                    Layout.fillWidth: true
                    message: backend.statusMessage
                    type: backend.statusType
                    progress: backend.progress
                }
            }
        }
    }
} 