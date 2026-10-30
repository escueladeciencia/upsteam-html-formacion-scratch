/* Generado por herramientas/construye-pasos.py: no lo edites a mano. */
window.TRO_PASOS = {
 "1": {
  "titulo": "Un petardo en la plaza",
  "sb3": "paso-01.sb3",
  "guiones": [
   {
    "guion": "bandera",
    "codigo": "when flag clicked\ngo to x: (0) y: (0)\nswitch costume to [mecha1 v]\nshow",
    "ids": [
     "p1",
     "p2",
     "p3",
     "p5"
    ],
    "nuevos": []
   }
  ]
 },
 "2": {
  "titulo": "La mecha se quema",
  "sb3": "paso-02.sb3",
  "guiones": [
   {
    "guion": "bandera",
    "codigo": "when flag clicked\ngo to x: (0) y: (0)\nswitch costume to [mecha1 v]\nshow\nrepeat (8)\n  wait (0.125) seconds\n  next costume\nend",
    "ids": [
     "p1",
     "p2",
     "p3",
     "p5",
     "p6",
     "p7",
     "p8"
    ],
    "nuevos": [
     "p6",
     "p7",
     "p8"
    ]
   }
  ]
 },
 "3-error": {
  "titulo": "¡PUM! al hacer clic (primera idea, con un error)",
  "sb3": "paso-03-error.sb3",
  "guiones": [
   {
    "guion": "bandera",
    "codigo": "when flag clicked\ngo to x: (0) y: (0)\nswitch costume to [mecha1 v]\nshow\nrepeat (8)\n  wait (0.125) seconds\n  next costume\nend",
    "ids": [
     "p1",
     "p2",
     "p3",
     "p5",
     "p6",
     "p7",
     "p8"
    ],
    "nuevos": []
   },
   {
    "guion": "clic",
    "codigo": "when this sprite clicked\nswitch costume to [pum v]\nstart sound [pum v]\nwait (0.3) seconds\nhide",
    "ids": [
     "p9",
     "p10",
     "p12",
     "p14",
     "p15"
    ],
    "nuevos": [
     "p9",
     "p10",
     "p12",
     "p14",
     "p15"
    ]
   }
  ]
 },
 "3": {
  "titulo": "¡PUM! al hacer clic",
  "sb3": "paso-03.sb3",
  "guiones": [
   {
    "guion": "bandera",
    "codigo": "when flag clicked\ngo to x: (0) y: (0)\nswitch costume to [mecha1 v]\nshow\nrepeat (8)\n  wait (0.125) seconds\n  next costume\nend",
    "ids": [
     "p1",
     "p2",
     "p3",
     "p5",
     "p6",
     "p7",
     "p8"
    ],
    "nuevos": []
   },
   {
    "guion": "clic",
    "codigo": "when this sprite clicked\nstop [otros programas en el objeto v]\nswitch costume to [pum v]\nstart sound [pum v]\nwait (0.3) seconds\nhide",
    "ids": [
     "p9",
     "p10",
     "p11",
     "p13",
     "p15",
     "p16"
    ],
    "nuevos": [
     "p9",
     "p10",
     "p11",
     "p13",
     "p15",
     "p16"
    ]
   }
  ]
 },
 "4": {
  "titulo": "Los decibelios: una variable",
  "sb3": "paso-04.sb3",
  "guiones": [
   {
    "guion": "bandera",
    "codigo": "when flag clicked\nset [decibelios v] to (0)\ngo to x: (0) y: (0)\nswitch costume to [mecha1 v]\nshow\nrepeat (8)\n  wait (0.125) seconds\n  next costume\nend",
    "ids": [
     "p1",
     "p2",
     "p3",
     "p4",
     "p6",
     "p7",
     "p8",
     "p9"
    ],
    "nuevos": [
     "p2"
    ]
   },
   {
    "guion": "clic",
    "codigo": "when this sprite clicked\nstop [otros programas en el objeto v]\nswitch costume to [pum v]\nstart sound [pum v]\nchange [decibelios v] by (100)\nwait (0.3) seconds\nhide",
    "ids": [
     "p10",
     "p11",
     "p12",
     "p14",
     "p16",
     "p17",
     "p18"
    ],
    "nuevos": [
     "p16"
    ]
   }
  ]
 },
 "5": {
  "titulo": "¿A tiempo o fallado?",
  "sb3": "paso-05.sb3",
  "guiones": [
   {
    "guion": "bandera",
    "codigo": "when flag clicked\nset [decibelios v] to (0)\ngo to x: (0) y: (0)\nswitch costume to [mecha1 v]\nshow\nrepeat (8)\n  wait (0.125) seconds\n  next costume\nend\nwait (0.2) seconds\nswitch costume to [fallado v]\nstart sound [fsss v]\nwait (0.5) seconds\nhide",
    "ids": [
     "p1",
     "p2",
     "p3",
     "p4",
     "p6",
     "p7",
     "p8",
     "p9",
     "p10",
     "p11",
     "p13",
     "p15",
     "p16"
    ],
    "nuevos": [
     "p10",
     "p11",
     "p13",
     "p15",
     "p16"
    ]
   },
   {
    "guion": "clic",
    "codigo": "when this sprite clicked\nif <(costume [número v]) > (6)> then\n  stop [otros programas en el objeto v]\n  switch costume to [pum v]\n  start sound [pum v]\n  change [decibelios v] by (100)\n  wait (0.3) seconds\n  hide\nend",
    "ids": [
     "p17",
     "p18",
     "p19",
     "p20",
     "p21",
     "p22",
     "p24",
     "p26",
     "p27",
     "p28"
    ],
    "nuevos": [
     "p18",
     "p19",
     "p20"
    ]
   }
  ]
 },
 "6": {
  "titulo": "Muchos petardos: clones",
  "sb3": "paso-06.sb3",
  "guiones": [
   {
    "guion": "bandera",
    "codigo": "when flag clicked\nhide\nset [decibelios v] to (0)\nrepeat (20)\n  go to x: (pick random (-180) to (180)) y: (pick random (-80) to (80))\n  create clone of [mí mismo v]\n  wait (1) seconds\nend",
    "ids": [
     "p1",
     "p2",
     "p3",
     "p4",
     "p5",
     "p6",
     "p7",
     "p8",
     "p10"
    ],
    "nuevos": [
     "p3",
     "p4",
     "p5",
     "p6",
     "p7",
     "p8",
     "p10"
    ]
   },
   {
    "guion": "clic",
    "codigo": "when this sprite clicked\nif <(costume [número v]) > (6)> then\n  stop [otros programas en el objeto v]\n  switch costume to [pum v]\n  start sound [pum v]\n  change [decibelios v] by (100)\n  wait (0.3) seconds\n  delete this clone\nend",
    "ids": [
     "p11",
     "p12",
     "p13",
     "p14",
     "p15",
     "p16",
     "p18",
     "p20",
     "p21",
     "p22"
    ],
    "nuevos": [
     "p22"
    ]
   },
   {
    "guion": "clon",
    "codigo": "when I start as a clone\nswitch costume to [mecha1 v]\ngo to [trasera v] layer\nshow\nrepeat (8)\n  wait (0.125) seconds\n  next costume\nend\nwait (0.2) seconds\nswitch costume to [fallado v]\nstart sound [fsss v]\nwait (0.5) seconds\ndelete this clone",
    "ids": [
     "p23",
     "p24",
     "p26",
     "p27",
     "p28",
     "p29",
     "p30",
     "p31",
     "p32",
     "p34",
     "p36",
     "p37"
    ],
    "nuevos": [
     "p23",
     "p26",
     "p37"
    ]
   }
  ]
 },
 "7": {
  "titulo": "Con música",
  "sb3": "paso-07.sb3",
  "guiones": [
   {
    "guion": "bandera",
    "codigo": "when flag clicked\nhide\nset [decibelios v] to (0)\nstart sound [pasodoble v]\nwait (3) seconds\nrepeat (100)\n  go to x: (pick random (-180) to (180)) y: (pick random (-80) to (80))\n  create clone of [mí mismo v]\n  wait (0.5) seconds\nend",
    "ids": [
     "p1",
     "p2",
     "p3",
     "p4",
     "p6",
     "p7",
     "p8",
     "p9",
     "p10",
     "p11",
     "p13"
    ],
    "nuevos": [
     "p4",
     "p6",
     "p7",
     "p13"
    ]
   },
   {
    "guion": "clic",
    "codigo": "when this sprite clicked\nif <(costume [número v]) > (6)> then\n  stop [otros programas en el objeto v]\n  switch costume to [pum v]\n  start sound [pum v]\n  change [decibelios v] by (100)\n  wait (0.3) seconds\n  delete this clone\nend",
    "ids": [
     "p14",
     "p15",
     "p16",
     "p17",
     "p18",
     "p19",
     "p21",
     "p23",
     "p24",
     "p25"
    ],
    "nuevos": []
   },
   {
    "guion": "clon",
    "codigo": "when I start as a clone\nswitch costume to [mecha1 v]\ngo to [trasera v] layer\nshow\nrepeat (8)\n  wait (0.125) seconds\n  next costume\nend\nwait (0.2) seconds\nswitch costume to [fallado v]\nstart sound [fsss v]\nwait (0.5) seconds\ndelete this clone",
    "ids": [
     "p26",
     "p27",
     "p29",
     "p30",
     "p31",
     "p32",
     "p33",
     "p34",
     "p35",
     "p37",
     "p39",
     "p40"
    ],
    "nuevos": []
   }
  ]
 },
 "8": {
  "titulo": "Al ritmo: cronómetro y lista",
  "sb3": "paso-08.sb3",
  "guiones": [
   {
    "guion": "bandera",
    "codigo": "when flag clicked\nhide\nset [decibelios v] to (0)\nset [n v] to (1)\nstart sound [pasodoble v]\nreset timer\nrepeat (length of [tiempos v])\n  wait until <(timer) > ((item (n :: variables) of [tiempos v]) - (1))>\n  go to x: (pick random (-180) to (180)) y: (pick random (-80) to (80))\n  create clone of [mí mismo v]\n  change [n v] by (1)\nend",
    "ids": [
     "p1",
     "p2",
     "p3",
     "p4",
     "p5",
     "p7",
     "p8",
     "p9",
     "p10",
     "p11",
     "p12",
     "p13",
     "p14",
     null,
     "p15",
     "p16",
     "p17",
     "p18",
     "p20"
    ],
    "nuevos": [
     "p4",
     "p7",
     "p8",
     "p9",
     "p10",
     "p11",
     "p12",
     "p13",
     "p14",
     "p20"
    ]
   },
   {
    "guion": "clic",
    "codigo": "when this sprite clicked\nif <(costume [número v]) > (6)> then\n  stop [otros programas en el objeto v]\n  switch costume to [pum v]\n  start sound [pum v]\n  change [decibelios v] by (100)\n  wait (0.3) seconds\n  delete this clone\nend",
    "ids": [
     "p21",
     "p22",
     "p23",
     "p24",
     "p25",
     "p26",
     "p28",
     "p30",
     "p31",
     "p32"
    ],
    "nuevos": []
   },
   {
    "guion": "clon",
    "codigo": "when I start as a clone\nswitch costume to [mecha1 v]\ngo to [trasera v] layer\nshow\nrepeat (8)\n  wait (0.125) seconds\n  next costume\nend\nwait (0.2) seconds\nswitch costume to [fallado v]\nstart sound [fsss v]\nwait (0.5) seconds\ndelete this clone",
    "ids": [
     "p33",
     "p34",
     "p36",
     "p37",
     "p38",
     "p39",
     "p40",
     "p41",
     "p42",
     "p44",
     "p46",
     "p47"
    ],
    "nuevos": []
   }
  ]
 },
 "9": {
  "titulo": "Modo pirotécnico: graba tu mascletà",
  "sb3": "paso-09.sb3",
  "guiones": [
   {
    "guion": "bandera",
    "codigo": "when flag clicked\nhide\nset [decibelios v] to (0)\nset [n v] to (1)\nstart sound [pasodoble v]\nreset timer\nrepeat (length of [tiempos v])\n  wait until <(timer) > ((item (n :: variables) of [tiempos v]) - (1))>\n  go to x: (item (n :: variables) of [x v]) y: (item (n :: variables) of [y v])\n  create clone of [mí mismo v]\n  change [n v] by (1)\nend",
    "ids": [
     "p1",
     "p2",
     "p3",
     "p4",
     "p5",
     "p7",
     "p8",
     "p9",
     "p10",
     "p11",
     "p12",
     "p13",
     "p14",
     null,
     "p15",
     "p16",
     null,
     "p17",
     null,
     "p18",
     "p20"
    ],
    "nuevos": [
     "p15",
     "p16",
     "p17"
    ]
   },
   {
    "guion": "clic",
    "codigo": "when this sprite clicked\nif <(costume [número v]) > (6)> then\n  stop [otros programas en el objeto v]\n  switch costume to [pum v]\n  start sound [pum v]\n  change [decibelios v] by (100)\n  wait (0.3) seconds\n  delete this clone\nend",
    "ids": [
     "p21",
     "p22",
     "p23",
     "p24",
     "p25",
     "p26",
     "p28",
     "p30",
     "p31",
     "p32"
    ],
    "nuevos": []
   },
   {
    "guion": "clon",
    "codigo": "when I start as a clone\nswitch costume to [mecha1 v]\ngo to [trasera v] layer\nshow\nrepeat (8)\n  wait (0.125) seconds\n  next costume\nend\nwait (0.2) seconds\nswitch costume to [fallado v]\nstart sound [fsss v]\nwait (0.5) seconds\ndelete this clone",
    "ids": [
     "p33",
     "p34",
     "p36",
     "p37",
     "p38",
     "p39",
     "p40",
     "p41",
     "p42",
     "p44",
     "p46",
     "p47"
    ],
    "nuevos": []
   },
   {
    "guion": "tecla g",
    "codigo": "when [g v] key pressed\ndelete all of [tiempos v]\ndelete all of [x v]\ndelete all of [y v]\nstop all sounds\nstart sound [pasodoble v]\nreset timer",
    "ids": [
     "p48",
     "p49",
     "p50",
     "p51",
     "p52",
     "p53",
     "p55"
    ],
    "nuevos": [
     "p48",
     "p49",
     "p50",
     "p51",
     "p52",
     "p53",
     "p55"
    ]
   },
   {
    "guion": "tecla espacio",
    "codigo": "when [espacio v] key pressed\nadd (timer) to [tiempos v]\nadd (mouse x) to [x v]\nadd (mouse y) to [y v]",
    "ids": [
     "p56",
     "p57",
     "p58",
     "p59",
     "p60",
     "p61",
     "p62"
    ],
    "nuevos": [
     "p56",
     "p57",
     "p58",
     "p59",
     "p60",
     "p61",
     "p62"
    ]
   }
  ]
 },
 "10": {
  "titulo": "Remate: traca, pantallas y final",
  "sb3": "paso-10.sb3",
  "guiones": [
   {
    "guion": "bandera",
    "codigo": "when flag clicked\nswitch backdrop to [plaza v]\nhide\nset [decibelios v] to (0)\nset [traca v] to (0)\nset [n v] to (1)\nstart sound [pasodoble v]\nreset timer\nrepeat (length of [tiempos v])\n  wait until <(timer) > ((item (n :: variables) of [tiempos v]) - (1))>\n  go to x: (item (n :: variables) of [x v]) y: (item (n :: variables) of [y v])\n  create clone of [mí mismo v]\n  change [n v] by (1)\nend\nwait until <(timer) > (62)>\nswitch backdrop to [final v]",
    "ids": [
     "p1",
     "p2",
     "p4",
     "p5",
     "p6",
     "p7",
     "p8",
     "p10",
     "p11",
     "p12",
     "p13",
     "p14",
     "p15",
     "p16",
     "p17",
     null,
     "p18",
     "p19",
     null,
     "p20",
     null,
     "p21",
     "p23",
     "p24",
     "p25",
     "p26",
     "p27"
    ],
    "nuevos": [
     "p2",
     "p6",
     "p24",
     "p25",
     "p26",
     "p27"
    ]
   },
   {
    "guion": "clic",
    "codigo": "when this sprite clicked\nif <(costume [número v]) > (6)> then\n  stop [otros programas en el objeto v]\n  switch costume to [pum v]\n  start sound [pum v]\n  change [decibelios v] by (100)\n  change [traca v] by (1)\n  wait (0.3) seconds\n  delete this clone\nend",
    "ids": [
     "p29",
     "p30",
     "p31",
     "p32",
     "p33",
     "p34",
     "p36",
     "p38",
     "p39",
     "p40",
     "p41"
    ],
    "nuevos": [
     "p39"
    ]
   },
   {
    "guion": "clon",
    "codigo": "when I start as a clone\nswitch costume to [mecha1 v]\ngo to [trasera v] layer\nshow\nrepeat (8)\n  wait (0.125) seconds\n  next costume\nend\nwait (0.2) seconds\nswitch costume to [fallado v]\nstart sound [fsss v]\nset [traca v] to (0)\nwait (0.5) seconds\ndelete this clone",
    "ids": [
     "p42",
     "p43",
     "p45",
     "p46",
     "p47",
     "p48",
     "p49",
     "p50",
     "p51",
     "p53",
     "p55",
     "p56",
     "p57"
    ],
    "nuevos": [
     "p55"
    ]
   },
   {
    "guion": "tecla g",
    "codigo": "when [g v] key pressed\ndelete all of [tiempos v]\ndelete all of [x v]\ndelete all of [y v]\nstop all sounds\nstart sound [pasodoble v]\nreset timer",
    "ids": [
     "p58",
     "p59",
     "p60",
     "p61",
     "p62",
     "p63",
     "p65"
    ],
    "nuevos": []
   },
   {
    "guion": "tecla espacio",
    "codigo": "when [espacio v] key pressed\nadd (timer) to [tiempos v]\nadd (mouse x) to [x v]\nadd (mouse y) to [y v]",
    "ids": [
     "p66",
     "p67",
     "p68",
     "p69",
     "p70",
     "p71",
     "p72"
    ],
    "nuevos": []
   }
  ]
 }
};
