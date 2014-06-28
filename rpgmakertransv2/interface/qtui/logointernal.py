"""
logointernal
************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Embeds the logo into the executable
"""

LOGOINTERNAL = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="32"
   height="32"
   id="svg2"
   version="1.1"
   inkscape:version="0.48+devel r"
   viewBox="0 0 32 32"
   sodipodi:docname="rpgtranslogo.svg">
  <defs
     id="defs4">
    <filter
       height="1.3"
       width="1.3"
       y="-0.15"
       x="-0.15"
       inkscape:menu-tooltip="Silk carpet texture, horizontal stripes"
       inkscape:menu="Textures"
       inkscape:label="Silk Carpet"
       style="color-interpolation-filters:sRGB;"
       id="filter5227">
      <feTurbulence
         type="turbulence"
         numOctaves="2"
         baseFrequency="0.01 0.11"
         seed="10"
         id="feTurbulence5229" />
      <feColorMatrix
         result="result5"
         values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 1.3 0 "
         id="feColorMatrix5231" />
      <feComposite
         in="SourceGraphic"
         operator="out"
         in2="result5"
         id="feComposite5233" />
      <feMorphology
         operator="dilate"
         radius="1.3"
         result="result3"
         id="feMorphology5235" />
      <feTurbulence
         numOctaves="3"
         baseFrequency="0.08 0.05"
         type="fractalNoise"
         seed="7"
         result="result6"
         id="feTurbulence5237" />
      <feGaussianBlur
         stdDeviation="0.5"
         result="result7"
         id="feGaussianBlur5239" />
      <feDisplacementMap
         in="result3"
         xChannelSelector="R"
         yChannelSelector="G"
         scale="3"
         result="result4"
         in2="result7"
         id="feDisplacementMap5241" />
      <feComposite
         in="result4"
         k1="1"
         result="result2"
         operator="arithmetic"
         in2="result4"
         k2="1"
         id="feComposite5243" />
      <feBlend
         in2="result4"
         mode="normal"
         in="result2"
         id="feBlend5245" />
    </filter>
  </defs>
  <sodipodi:namedview
     id="base"
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1.0"
     inkscape:pageopacity="0.0"
     inkscape:pageshadow="2"
     inkscape:zoom="31.678384"
     inkscape:cx="18.725022"
     inkscape:cy="15.002464"
     inkscape:document-units="px"
     inkscape:current-layer="layer1"
     showgrid="false"
     showguides="false"
     inkscape:window-width="1920"
     inkscape:window-height="1002"
     inkscape:window-x="0"
     inkscape:window-y="34"
     inkscape:window-maximized="1"
     fit-margin-top="0"
     fit-margin-left="0"
     fit-margin-right="0"
     fit-margin-bottom="0" />
  <metadata
     id="metadata7">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <g
     inkscape:label="Layer 1"
     inkscape:groupmode="layer"
     id="layer1"
     transform="translate(-79.999993,-257.36218)">
    <path
       inkscape:connector-curvature="0"
       style="opacity:1;fill:#8181d8;fill-opacity:1;stroke:none;stroke-width:0.30000001;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
       d="m 81.67741,257.84656 c -0.678332,0 -1.224609,0.54627 -1.224609,1.2246 l 0,14.29102 31.031249,0 0,-14.29102 c 0,-0.67833 -0.54628,-1.2246 -1.22461,-1.2246 l -28.58203,0 z"
       id="rect4151" />
    <g
       style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-size:10px;line-height:125%;font-family:Sans;-inkscape-font-specification:'Sans Bold';letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.30000001;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
       id="text4137">
      <path
         d="m 91.286102,264.25424 -2.565307,0 q -0.06592,2.29065 -0.774536,3.58704 -0.873414,1.604 -2.790528,2.62024 l -0.675659,-0.69763 q 2.04895,-0.94483 2.790527,-2.64222 0.466919,-1.08764 0.516358,-2.86743 l -2.72461,0 q -0.708618,1.43921 -1.977539,2.62024 l -0.664673,-0.60425 q 2.087403,-1.88965 2.713624,-4.98779 l 0.862426,0.19226 q -0.219726,1.01074 -0.571289,1.95557 l 5.861206,0 0,0.82397 z m -1.104126,-1.23047 q -0.444946,-0.74707 -1.071167,-1.40625 l 0.587769,-0.36804 q 0.609741,0.59326 1.137085,1.3678 l -0.653687,0.40649 z m 1.126099,-0.54931 q -0.45044,-0.71411 -1.148071,-1.36231 l 0.593261,-0.38452 q 0.604248,0.52734 1.19751,1.32935 l -0.6427,0.41748 z"
         style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-size:11.25px;font-family:Sans;-inkscape-font-specification:'Sans Bold';letter-spacing:-1.29999995px;stroke:#000000;stroke-width:0.30000001;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
         id="path4194" />
      <path
         d="m 91.661517,265.28696 9.179073,0 0,0.90088 -9.179073,0 0,-0.90088 z"
         style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-size:11.25px;font-family:Sans;-inkscape-font-specification:'Sans Bold';letter-spacing:-1.29999995px;stroke:#000000;stroke-width:0.30000001;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
         id="path4196" />
      <path
         d="m 100.7381,268.44553 0.19226,-0.011 0.29114,-0.011 q 0.29663,-0.0165 0.66468,-0.0384 0.26367,-0.011 0.32409,-0.0165 1.48316,-3.43323 2.47742,-6.62475 l 0.94482,0.31311 q -0.97229,2.92785 -2.41699,6.23474 2.69714,-0.23072 4.64172,-0.52185 -0.80749,-1.18653 -1.74133,-2.30164 l 0.79651,-0.43945 q 1.67542,1.99402 2.92786,4.08142 l -0.82398,0.56579 q -0.49438,-0.8789 -0.69763,-1.18103 -3.52112,0.62073 -7.20703,0.94483 l -0.37354,-0.99426 z"
         style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-size:11.25px;font-family:Sans;-inkscape-font-specification:'Sans Bold';letter-spacing:-1.29999995px;stroke:#000000;stroke-width:0.30000001;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
         id="path4198" />
    </g>
    <path
       inkscape:connector-curvature="0"
       style="opacity:1;fill:#e11e1e;fill-opacity:1;stroke:none;stroke-width:0.30000001;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
       d="m 80.452801,273.36218 0,14.29102 c 0,0.67833 0.546277,1.22461 1.224609,1.22461 l 28.58203,0 c 0.67833,0 1.22461,-0.54628 1.22461,-1.22461 l 0,-14.29102 -31.031249,0 z"
       id="rect4153" />
    <rect
       style="opacity:1;fill:#c738c7;fill-opacity:1;stroke:none;stroke-width:1;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
       id="rect4180"
       width="32"
       height="4"
       x="79.999992"
       y="271.36218" />
    <g
       style="font-style:normal;font-weight:normal;font-size:9.71279144px;line-height:0%;font-family:Sans;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
       id="text4141">
      <path
         d="m 85.355537,282.47159 q -0.406494,0.53833 -0.895385,0.79101 -0.488892,0.25269 -1.131592,0.25269 -1.126099,0 -1.862183,-0.8844 -0.736084,-0.88989 -0.736084,-2.26318 0,-1.37879 0.736084,-2.25769 0.736084,-0.8844 1.862183,-0.8844 0.6427,0 1.131592,0.25268 0.488891,0.25269 0.895385,0.79651 l 0,-0.91186 1.977539,0 0,5.53161 q 0,1.48316 -0.939331,2.26319 -0.933837,0.78552 -2.713623,0.78552 -0.576782,0 -1.115112,-0.0879 -0.53833,-0.0879 -1.082153,-0.26917 l 0,-1.53259 q 0.516357,0.29663 1.010742,0.43945 0.494385,0.14832 0.994263,0.14832 0.966797,0 1.417236,-0.42298 0.450439,-0.42297 0.450439,-1.32385 l 0,-0.42297 z m -1.296386,-3.82874 q -0.609742,0 -0.950318,0.45044 -0.340576,0.45044 -0.340576,1.27442 0,0.84594 0.32959,1.2854 0.32959,0.43396 0.961304,0.43396 0.615234,0 0.95581,-0.45044 0.340576,-0.45044 0.340576,-1.26892 0,-0.82398 -0.340576,-1.27442 -0.340576,-0.45044 -0.95581,-0.45044 z"
         style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-size:11.25px;line-height:0%;font-family:Sans;-inkscape-font-specification:'Sans Bold';letter-spacing:-1.15999997px"
         id="path4185" />
      <path
         d="m 90.83128,280.74673 q -0.615235,0 -0.928345,0.20874 -0.307617,0.20875 -0.307617,0.61524 0,0.37353 0.247192,0.58777 0.252686,0.20874 0.697632,0.20874 0.55481,0 0.933838,-0.39551 0.379028,-0.401 0.379028,-0.99976 l 0,-0.22522 -1.021728,0 z m 3.00476,-0.74157 0,3.51013 -1.983032,0 0,-0.91187 q -0.395508,0.56031 -0.889892,0.81849 -0.494385,0.25268 -1.203003,0.25268 -0.955811,0 -1.554566,-0.55481 -0.593261,-0.5603 -0.593261,-1.45019 0,-1.08216 0.741577,-1.58753 0.74707,-0.50537 2.340088,-0.50537 l 1.159057,0 0,-0.15381 q 0,-0.46692 -0.368042,-0.68115 -0.368042,-0.21973 -1.148071,-0.21973 -0.631714,0 -1.175537,0.12635 -0.543823,0.12634 -1.010742,0.37902 l 0,-1.49963 q 0.631714,-0.15381 1.268921,-0.23071 0.637207,-0.0824 1.274414,-0.0824 1.664428,0 2.400512,0.65918 0.741577,0.65369 0.741577,2.13135 z"
         style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-size:11.25px;line-height:0%;font-family:Sans;-inkscape-font-specification:'Sans Bold';letter-spacing:-1.15999997px"
         id="path4187" />
      <path
         d="m 100.21815,278.38467 q 0.37354,-0.57128 0.8844,-0.86792 0.51636,-0.30212 1.1316,-0.30212 1.06018,0 1.61499,0.65369 0.55481,0.65368 0.55481,1.90063 l 0,3.74634 -1.97754,0 0,-3.20801 q 0.005,-0.0714 0.005,-0.14831 0.005,-0.0769 0.005,-0.21973 0,-0.65369 -0.19226,-0.94482 -0.19226,-0.29664 -0.62073,-0.29664 -0.5603,0 -0.86792,0.46143 -0.30212,0.46143 -0.31311,1.33484 l 0,3.02124 -1.977534,0 0,-3.20801 q 0,-1.02173 -0.175782,-1.31286 -0.175781,-0.29664 -0.62622,-0.29664 -0.565796,0 -0.873413,0.46692 -0.307618,0.46143 -0.307618,1.32386 l 0,3.02673 -1.977539,0 0,-6.15234 1.977539,0 0,0.90087 q 0.362549,-0.52185 0.829468,-0.78552 0.472412,-0.26367 1.038208,-0.26367 0.637207,0 1.126099,0.30762 0.488891,0.30761 0.741572,0.86242 z"
         style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-size:11.25px;line-height:0%;font-family:Sans;-inkscape-font-specification:'Sans Bold';letter-spacing:-1.15999997px"
         id="path4189" />
      <path
         d="m 111.23101,280.42264 0,0.5603 -4.59778,0 q 0.0714,0.69214 0.49988,1.03821 0.42846,0.34607 1.19751,0.34607 0.62072,0 1.26892,-0.18128 0.65368,-0.18676 1.34033,-0.5603 l 0,1.51611 q -0.69763,0.26368 -1.39526,0.39551 -0.69764,0.13733 -1.39527,0.13733 -1.66992,0 -2.59827,-0.84595 -0.92285,-0.85144 -0.92285,-2.38403 0,-1.50513 0.90638,-2.36755 0.91186,-0.86243 2.50488,-0.86243 1.45019,0 2.31811,0.87341 0.87342,0.87342 0.87342,2.3346 z m -2.02149,-0.65369 q 0,-0.5603 -0.32959,-0.90088 -0.32409,-0.34607 -0.85144,-0.34607 -0.57129,0 -0.92834,0.3241 -0.35706,0.3186 -0.44495,0.92285 l 2.55432,0 z"
         style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-size:11.25px;line-height:0%;font-family:Sans;-inkscape-font-specification:'Sans Bold';letter-spacing:-1.15999997px"
         id="path4191" />
    </g>
    <rect
       style="opacity:1;fill:none;fill-opacity:1;stroke:#000000;stroke-width:0.969697;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
       id="rect4155"
       width="31.030304"
       height="31.030304"
       x="80.48484"
       y="257.84702"
       ry="1.2244273" />
  </g>
</svg>"""
