import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Rectangle {
    id: root
    color: surfaceColor
    radius: 8

    signal filesSelected(var files)
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        Text {
            text: "数据文件"
            color: textColor
            font.pixelSize: 18
            font.weight: Font.Medium
        }

        Rectangle {
            Layout.fillWidth: true
            height: 120
            color: Qt.rgba(1, 1, 1, 0.05)
            border.color: Qt.rgba(1, 1, 1, 0.1)
            border.width: 2
            radius: 6

            ColumnLayout {
                anchors.centerIn: parent
                spacing: 10

                Image {
                    Layout.alignment: Qt.AlignHCenter
                    source: "qrc:/icons/upload.svg"
                    width: 32
                    height: 32
                }

                Text {
                    text: "拖放 .raw 文件到这里\n或者"
                    color: textColor
                    horizontalAlignment: Text.AlignHCenter
                }

                Button {
                    text: "选择文件"
                    onClicked: fileDialog.open()
                }
            }

            DropArea {
                anchors.fill: parent
                onDropped: function(drop) {
                    if (drop.hasUrls) {
                        root.filesSelected(drop.urls)
                    }
                }
            }
        }
    }

    FileDialog {
        id: fileDialog
        title: "选择 .raw 文件"
        nameFilters: ["Waters RAW files (*.raw)"]
        fileMode: FileDialog.OpenFiles
        onAccepted: root.filesSelected(selectedFiles)
    }
} 