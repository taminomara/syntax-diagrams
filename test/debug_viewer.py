from flask import Flask, request, render_template_string
import syntax_diagrams as rr
import yaml

app = Flask(__name__)

# HTML template with embedded CSS for better styling
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Syntax Diagram Debug Viewer</title>
    <style>
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        form {
            margin-bottom: 20px;
        }

        label {
            font-weight: bold;
            color: #333;
        }

        textarea {
            width: 100%;
            min-height: 100px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
        }

        button {
            background-color: #007acc;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
        }

        button:hover {
            background-color: #005cc5;
        }

        .dbg-area {
            display: flex;
            gap: 3px;
        }

        .result-container {
            flex: 1 1 50%;
            position: relative;
        }

        #result-overlay {
            position: absolute;
            top: 0;
            left: 0;
            pointer-events: none;
        }

        #result-overlay svg :not(:is(g)) {
            display: none
        }

        #dbg-view, #dbg-view-elem {
            flex: 0 0 25%;
            width: 300px;
            max-height: 400px;
            overflow-x: scroll;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 12px;
        }

        .tree-node {
            position: relative;
            margin-left: 10px;
            border-left: 1px solid #f5f5f5;
        }

        .element-info {
            cursor: pointer;
            padding: 3px 5px;
        }

        .element-info:hover {
            background-color: #f5f5f5;
        }

        .element-info.selected {
            background-color: #007acc;
            color: white;
        }

        .data-attribute-container, .structure-tree {
            width: max-content;
        }

        .data-attribute {
            padding: 3px 5px;
            margin: 2px 0;
            background-color: #f5f5f5;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 12px;
        }

        .attr-name {
            font-weight: bold;
            color: #d73a49;
        }

        .attr-value {
            color: #005cc5;
        }

        .debug-highlight>*,
        .debug-highlight>.node *,
        .debug-highlight>.group * {
            display: inherit !important;
        }
        .debug-highlight>.dbg-display {
            stroke: #005cc5;
            stroke-width: 1px;
            stroke-dasharray: 2;
            opacity: 0.5;
        }
        .debug-highlight>.dbg-content {
            stroke: #005cc5;
            stroke-width: 1px;
        }
        .debug-highlight>.dbg-content-main {
            stroke: #005cc5;
            stroke-width: 1px;
        }
        .debug-highlight>.dbg-padding {
            stroke: #005cc5;
            stroke-width: 1px;
        }
        .debug-highlight>.dbg-margin {
            stroke: #005cc5;
            stroke-width: 1px;
            stroke-dasharray: 4;
        }
        .debug-highlight>.dbg-position {
            stroke: #005cc5;
            stroke-width: 1px;
        }
        .debug-highlight>.dbg-position.dbg-primary-pos {
            stroke: #d73a49;
        }
        .debug-highlight>.dbg-position.dbg-isolated-pos,
        .debug-highlight>.dbg-isolated-line {
            stroke: #d73a49;
        }
        .debug-highlight>.dbg-alternative-pos {
            stroke: #1bbc4e;
        }
        .debug-highlight>path,
        .debug-highlight>.node rect,
        .debug-highlight>.group rect {
            stroke: #dd9000;
        }
        .debug-highlight>.dbg-ridge-line {
            stroke: #007acc;
            stroke-width: 1px;
            fill: #007acc;
            opacity: 0.2;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Syntax Diagram Debug Viewer</h1>
        <form method="POST">
            <label for="diag_input">Enter YAML diagram description:</label>
            <textarea name="diag_input" id="diag_input">{{ diag_input or '' }}</textarea>
            <button type="submit">Process</button>
        </form>
        <div class="dbg-area">
            {% if svg %}
            <div class="result-container">
                <div id="result">
                    {{ svg | safe }}
                </div>
                <div id="result-overlay">
                    {{ svg | safe }}
                </div>
            </div>
            <div id="dbg-view">
            </div>
            <div id="dbg-view-elem">
            </div>
            {% endif %}
        </div>
    </div>
    <script>
        // Track the currently selected element
        let selectedElement = null;

        function displayElementStructure() {
            const result = document.getElementById('result-overlay');
            if (!result) {
                return;
            }

            const debugView = document.getElementById('dbg-view');
            if (!debugView) {
                return;
            }

            const debugViewElem = document.getElementById('dbg-view-elem');
            if (!debugViewElem) {
                return;
            }

            debugViewElem.innerHTML = '';

            const elemElements = result.querySelectorAll('.elem');

            const structureContainer = document.createElement('div');
            structureContainer.className = 'structure-tree';

            const rootElements = Array.from(elemElements).filter(elem => {
                return !elem.parentElement.closest('.elem');
            });

            rootElements.forEach((rootElem, index) => {
                const treeNode = createTreeNode(rootElem, 0, debugViewElem);
                structureContainer.appendChild(treeNode);
            });

            debugView.appendChild(structureContainer);
        }

        function createTreeNode(element, depth, debugViewElem) {
            const nodeDiv = document.createElement('div');
            nodeDiv.className = 'tree-node';

            const elementInfo = document.createElement('div');
            elementInfo.className = 'element-info';
            elementInfo.textContent = element.dataset.dbgElem;

            // Handle mouse enter - show debug info if not already selected
            elementInfo.addEventListener('mouseenter', () => {
                // Don't overwrite data if an element is locked/selected
                if (selectedElement !== element) {
                    if (!selectedElement) {
                        document.querySelectorAll('.debug-highlight').forEach(el => {
                            el.classList.remove('debug-highlight');
                        });
                        element.classList.add('debug-highlight');

                        // Show debug info
                        showElementDebugInfo(element, debugViewElem);
                    }
                }
            });

            // Handle click - toggle selection state
            elementInfo.addEventListener('click', () => {
                if (selectedElement === element) {
                    // Unselect if clicking the same element
                    selectedElement = null;
                    element.classList.remove('debug-highlight');
                    elementInfo.classList.remove('selected');
                    debugViewElem.innerHTML = '';
                } else {
                    // Select this element
                    if (selectedElement) {
                        selectedElement.classList.remove('debug-highlight');
                        // Find and remove selected class from previous element info
                        document.querySelectorAll('.element-info.selected').forEach(el => {
                            el.classList.remove('selected');
                        });
                    }
                    selectedElement = element;
                    element.classList.add('debug-highlight');
                    elementInfo.classList.add('selected');

                    // Show debug info
                    showElementDebugInfo(element, debugViewElem);
                }
            });

            // Extract function to show debug info to avoid code duplication
            function showElementDebugInfo(element, debugViewElem) {
                // Populate dbg-view-elem with all data attributes
                debugViewElem.innerHTML = '';

                const attributesContainer = document.createElement('div');
                attributesContainer.className = 'data-attribute-container';

                // Get all data attributes from the element
                const dataAttributes = {};
                for (let attr of element.attributes) {
                    if (attr.name.startsWith('data-')) {
                        const cleanName = attr.name.slice(9);
                        dataAttributes[cleanName] = attr.value;
                    }
                }

                // Display each data attribute
                Object.keys(dataAttributes).forEach(attrName => {
                    const attrDiv = document.createElement('div');
                    attrDiv.className = 'data-attribute';

                    // Create elements instead of using innerHTML to avoid potential XSS
                    const nameSpan = document.createElement('span');
                    nameSpan.className = 'attr-name';
                    nameSpan.textContent = attrName + ':';

                    const valueSpan = document.createElement('span');
                    valueSpan.className = 'attr-value';
                    valueSpan.innerHTML = dataAttributes[attrName];

                    attrDiv.appendChild(nameSpan);
                    attrDiv.appendChild(document.createTextNode(' '));
                    attrDiv.appendChild(valueSpan);

                    attributesContainer.appendChild(attrDiv);
                });

                if (Object.keys(dataAttributes).length === 0) {
                    const noDataDiv = document.createElement('div');
                    noDataDiv.className = 'data-attribute';
                    noDataDiv.textContent = 'No data attributes found';
                    attributesContainer.appendChild(noDataDiv);
                }

                debugViewElem.appendChild(attributesContainer);
            }

            elementInfo.addEventListener('mouseleave', () => {
                // Only clear highlight and debug info if this element is not selected
                if (selectedElement !== element) {
                    element.classList.remove('debug-highlight');
                    if (!selectedElement) {
                        debugViewElem.innerHTML = '';
                    }
                }
            });

            nodeDiv.appendChild(elementInfo);

            const childElems = Array.from(element.querySelectorAll('.elem')).filter(child => {
                return child.parentElement.closest('.elem') === element;
            });

            childElems.forEach((childElem, index) => {
                const childNode = createTreeNode(childElem, depth + 1, debugViewElem);
                nodeDiv.appendChild(childNode);
            });

            return nodeDiv;
        }

        displayElementStructure();
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    diag_input = ''

    if request.method == 'POST':
        diag_input = request.form.get('diag_input', '').strip()
        diag = yaml.safe_load(diag_input)
        svg = rr.render_svg(diag, max_width=600)
        return render_template_string(HTML_TEMPLATE, svg=svg, diag_input=diag_input)

    return render_template_string(HTML_TEMPLATE, svg=None, diag_input=diag_input)

if __name__ == '__main__':
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
