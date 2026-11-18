# Form, anatomy and stylisation (`form-and-anatomy.md`)

How to sculpt shapes that read: big to small, the landmarks people recognise, creatures that could live, and how far to
break symmetry. Marks: **[S]** sourced (Sources at the end), **[R]** a rule of thumb teachers quote, **[D]** our
default with no pro number found (test it).

Reading map: 1 form hierarchy, 2 heads and faces, 3 bodies, 4 creatures, 5 asymmetry, 6 stylisation, 7 the agent's
three routes.

## 1. Form hierarchy

Primary (gesture, silhouette, big masses, proportion), secondary (muscle groups, planes, folds, landmarks), tertiary
(pores, wrinkles, scratches, weave). Detail on a wrong big form is a well-textured mistake [R].

1. Block out at real scale, 5k to 20k faces [D], from separate simple volumes (spheres, boxes, cylinders) per mass.
2. Unify with Voxel Remesh while the forms still move; Dyntopo only for local concept detail, never final topology [S].
3. Add Multires only once primary and secondary forms are done; no remesh after Multires starts, it destroys the levels [S].
4. Raise resolution only when the stroke you need is smaller than the current polygon spacing [R].
5. Never sculpt a child feature (ear, nostril, finger) before its parent mass reads right [R].

## 2. Heads and faces

- **Skull first:** cranium and a separate jaw mass, then 8 to 12 big planes (forehead, brow, temple, cheek front and
  side, nose bridge and side, mouth block, chin), Asaro-head style, so light can read the form [R].
- **Proportions (adult, front):** eye line at half the head height; one eye width between the eyes; brow to nose base
  and nose base to chin each a third of the face; the ear spans brow to nose base, behind the jaw [R]. Real scale:
  eyeball 23 to 24 mm, eye centres 62 to 65 mm apart [S].
- **Landmarks to hit on purpose:** brow ridge as a shelf, zygomatic arch sweeping to the ear, temple dip, nasolabial
  fold, jaw angle, chin mass, mouth corners tucked back behind a plane break [R].
- **Eyes are the most common AI failure:** eyeballs as separate spheres placed first; lids as shells with a visible
  rim (about 1 to 2 mm at real scale [D]); the upper lid covers the top of the iris, the lower lid touches it; a tear
  duct wedge at the inner corner; a cornea bulge over the iris [R].
- **Other giveaways:** lips need a philtrum, a vermilion border and corner depth; ears need helix, antihelix, concha
  and lobe; nostrils need alar wings and a rim, never plain holes [R].
- Stylised faces keep the structure and drop the small anatomy: `~/.claude/skills/model-characters/references/sculpt-stylized.md`.

## 3. Bodies

- **Gesture before anatomy:** a line of action, the ribcage (egg) and pelvis (box) tilted opposite ways on a flexible
  spine, limbs as tapered cylinders [R]. Correct muscles on a dead pose read as a mannequin.
- **Proportion in heads:** realistic 7.5 to 8 [S], heroic 8.5 or more, cartoon 3 to 6 [D].
- **Masses and landmarks:** pecs, deltoids, lats, traps; abdominal block and obliques over the iliac crest; glutes,
  quads (vastus lateralis sweep), calves; clavicle, scapula, 7th cervical vertebra; knee and elbow bones [R].
- **Realistic vs stylised:** realistic keeps every landmark with soft transitions; stylised merges them into 3 to 5
  shapes per limb and exaggerates one proportion only [R].
- Anatomy drawing references: `~/.claude/skills/draw-and-paint-art/references/anatomy-and-foreshortening.md`.

## 4. Creatures

1. Mash 2 or 3 real animals (a skull, a limb, a skin) and keep their joint logic [R].
2. Read the silhouette at thumbnail size before any detail.
3. Function: where each limb attaches, which way each joint bends, where muscle bulges and skin folds.
4. Detail by scale and region: big plates and folds, then ridges and scars, then pores and scale bumps; small scales at
   joints, large scales on flat areas, never a uniform scatter [R].
5. Wrinkles run across the direction of compression, at joints and along the motion axes, never as isotropic noise [R].

## 5. Asymmetry and life

- Symmetry on for the block-in, then off. Perfect mirrors read as artificial [S].
- Realistic faces: shift eye height, a mouth corner and a brow arch by roughly 1 to 3% of head size, nose slightly off
  axis [D]. `check_sculpt.py` reports the mirror error: under 0.05% means nobody broke the symmetry.
- Put it in the pose (head tilt, shoulder drop), the primary forms (one brow higher, jaw shifted), the secondary forms
  (folds differ per side) and the texture. Never by randomising vertices [R].
- Props get their asymmetry from damage and wear, not from bent shapes [R].

## 6. Stylisation

- One shape language per character and per scene: circles friendly, squares stable, triangles danger [R].
- Push and pull: exaggerate one proportion (head, hands, feet), keep the rest simple; fewer, larger, cleaner planes
  with a few sharp transitions as focal points [R].
- Named looks, by eye: soft rounded forms and clean surfaces (feature-animation look); angular painted planes with
  hand-painted shading (painterly look); chunky forms, bevel on every edge, little micro detail (stylised game look).
- Every asset in a scene keeps the same level of simplification; mixed levels read as mixed styles [R].

## 7. The agent's three routes

| Route | Strong at | Weak at | Rule |
| --- | --- | --- | --- |
| Procedural (bpy, displace, remesh, geometry nodes) | Tertiary noise, rocks, terrain | Primary and secondary forms | Build masses as explicit volumes (skin modifier, metaballs, ellipsoids, voxel-remesh union); add noise only after the silhouette passes. A noise displace on a sphere is the classic blob [R] |
| AI base mesh (Tripo Studio) | Primary form and proportion | Secondary planes, eyelids, mouth corners, mushy surface | Keep the silhouette, re-cut landmarks and hard planes, replace the mush with layered detail, never smooth the whole mesh to hide noise [R] |
| Hand strokes in sculpt mode | Everything, with a tablet | Headless agents | Big-form moves map to lattice, proportional edit, masked displace and shape keys in object or edit mode [D] |

Sources: Blender manual (Adaptive Sculpting, Multires); 80.lv "001agt queen realistic character production tips";
Proko lessons on proportions and the seven folds; Blender 2.91 sculpt notes; BlenderNation on Pablo Dobarro's tools;
novedge ZBrush tip on asymmetry. Research pass 2026-11-09; numbers marked [D] are untested defaults.
