import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: surfaceColor
    radius: 8

    signal parametersChanged(var params)

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        Text {
            text: "参数配置"
            color: textColor
            font.pixelSize: 18
            font.weight: Font.Medium
        }

        GridLayout {
            columns: 2
            columnSpacing: 20
            rowSpacing: 15

            Text {
                text: "峰高阈值"
                color: textColor
            }
            SpinBox {
                id: peakHeight
                from: 0
                to: 1000000
                stepSize: 1000
                value: 10000
                onValueChanged: updateParameters()
            }

            Text {
                text: "保留时间容差 (min)"
                color: textColor
            }
            SpinBox {
                id: rtTolerance
                from: 0
                to: 1000
                stepSize: 1
                value: 100
                onValueChanged: updateParameters()
            }

            // Add more parameters as needed
        }
    }

    function updateParameters() {
        parametersChanged({
            peakHeight: peakHeight.value,
            rtTolerance: rtTolerance.value / 1000
        })
    }
} 