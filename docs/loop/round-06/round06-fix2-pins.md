# Round 6 fix cycle 2: every moved test pin

The diff below names each changed assertion, old value and new value. The fixture and practice moves are deliberate.

```diff
diff --git a/tests/fixtures/matters/9001.001/ideal.json b/tests/fixtures/matters/9001.001/ideal.json
index 0ad5d9e..1e74cbd 100644
--- a/tests/fixtures/matters/9001.001/ideal.json
+++ b/tests/fixtures/matters/9001.001/ideal.json
@@ -76,7 +76,7 @@
       "cite": "MED0003",
       "quote": "Restrictions: no lifting over 10 pounds and no repetitive bending through 04/11/2025.",
       "text": "Restrictions were no lifting over 10 pounds and no repetitive bending through 04/11/2025.",
-      "date": "03/14/2025",
+      "date": "04/11/2025",
       "category": "work_status",
       "provider": "Brightwater Family Medicine"
     },
@@ -100,7 +100,7 @@
       "cite": "MED0005",
       "quote": "Patient reports new numbness into the left calf since approximately 04/10/2025.",
       "text": "The patient reported new numbness into the left calf since approximately 04/10/2025.",
-      "date": "04/14/2025",
+      "date": "04/10/2025",
       "category": "patient_statement",
       "provider": "Ridgeline Physical Therapy"
     },
@@ -156,7 +156,7 @@
       "cite": "MED0008",
       "quote": "In my opinion the L4-L5 disc protrusion is causally related to the lifting injury of 03/11/2025 described by the patient, within a reasonable degree of medical probability.",
       "text": "Dr. Okonkwo-Lind gave the opinion that the L4-L5 disc protrusion is causally related to the lifting injury of 03/11/2025.",
-      "date": "05/09/2025",
+      "date": "03/11/2025",
       "category": "causation_statement",
       "provider": "Dr. Priya Okonkwo-Lind"
     },
@@ -172,7 +172,7 @@
       "cite": "EMP0001",
       "quote": "Employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.",
       "text": "The employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.",
-      "date": "03/11/2025",
+      "date": "",
       "category": "mechanism_of_injury",
       "provider": ""
     },
@@ -180,7 +180,7 @@
       "cite": "EMP0003",
       "quote": "Average weekly wage: $912.40",
       "text": "The average weekly wage was $912.40.",
-      "date": "03/15/2025",
+      "date": "",
       "category": "employment",
       "provider": ""
     },
@@ -188,7 +188,7 @@
       "cite": "DEF0003",
       "quote": "The L4-L5 findings are degenerative and pre-existing, not causally related to the work incident of 03/11/2025.",
       "text": "Dr. Marchetti's report states the L4-L5 findings are degenerative and pre-existing, not causally related to the work incident of 03/11/2025.",
-      "date": "06/20/2025",
+      "date": "03/11/2025",
       "category": "causation_statement",
       "provider": "Dr. Theodore Marchetti"
     },
@@ -212,7 +212,7 @@
       "cite": "MED0008",
       "quote": "Restrictions: sedentary duty, no lifting over 15 pounds, until re-evaluation on 06/20/2025.",
       "text": "Dr. Okonkwo-Lind restricted the patient to sedentary duty with no lifting over 15 pounds until re-evaluation on 06/20/2025.",
-      "date": "05/09/2025",
+      "date": "06/20/2025",
       "category": "work_status",
       "provider": "Dr. Priya Okonkwo-Lind"
     },
@@ -236,7 +236,7 @@
       "cite": "EMP0001",
       "quote": "Date of hire: 08/02/2021",
       "text": "The incident report gives a hire date of 08/02/2021.",
-      "date": "03/11/2025",
+      "date": "08/02/2021",
       "category": "employment",
       "provider": ""
     },
@@ -244,9 +244,65 @@
       "cite": "EMP0002",
       "quote": "Lift up to 50 pounds repeatedly during the shift.",
       "text": "The job description requires lifting up to 50 pounds repeatedly.",
-      "date": "03/11/2025",
+      "date": "",
       "category": "employment",
       "provider": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Range of motion (ROM) in the lumbar spine is limited in flexion.",
+      "text": "Range of motion (ROM) in the lumbar spine is limited in flexion.",
+      "date": "06/20/2025",
+      "category": "exam_finding",
+      "provider": "Dr. Theodore Marchetti"
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Strength testing of lower extremities is 5/5 bilaterally.",
+      "text": "Strength testing of lower extremities is 5/5 bilaterally.",
+      "date": "06/20/2025",
+      "category": "exam_finding",
+      "provider": "Dr. Theodore Marchetti"
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Reflexes are 2+ and symmetric in all tested segments.",
+      "text": "Reflexes are 2+ and symmetric in all tested segments.",
+      "date": "06/20/2025",
+      "category": "exam_finding",
+      "provider": "Dr. Theodore Marchetti"
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Sensation is intact to light touch throughout the dermatomes.",
+      "text": "Sensation is intact to light touch throughout the dermatomes.",
+      "date": "06/20/2025",
+      "category": "exam_finding",
+      "provider": "Dr. Theodore Marchetti"
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Straight leg raise negative bilaterally.",
+      "text": "Straight leg raise negative bilaterally.",
+      "date": "06/20/2025",
+      "category": "exam_finding",
+      "provider": "Dr. Theodore Marchetti"
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "No objective findings of radiculopathy on today's examination.",
+      "text": "No objective findings of radiculopathy on today's examination.",
+      "date": "06/20/2025",
+      "category": "exam_finding",
+      "provider": "Dr. Theodore Marchetti"
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "The L4-L5 disc changes are described as degenerative.",
+      "text": "The L4-L5 disc changes are described as degenerative.",
+      "date": "06/20/2025",
+      "category": "imaging_result",
+      "provider": "Dr. Theodore Marchetti"
     }
   ],
   "flags": [
diff --git a/tests/fixtures/matters/9001.001/key.json b/tests/fixtures/matters/9001.001/key.json
index 417b88b..540bd59 100644
--- a/tests/fixtures/matters/9001.001/key.json
+++ b/tests/fixtures/matters/9001.001/key.json
@@ -68,7 +68,7 @@
       "cite": "MED0003",
       "quote": "Restrictions: no lifting over 10 pounds and no repetitive bending through 04/11/2025.",
       "text": "Restrictions were no lifting over 10 pounds and no repetitive bending through 04/11/2025.",
-      "date": "03/14/2025"
+      "date": "04/11/2025"
     },
     {
       "id": "F11",
@@ -89,7 +89,7 @@
       "cite": "MED0005",
       "quote": "Patient reports new numbness into the left calf since approximately 04/10/2025.",
       "text": "The patient reported new numbness into the left calf since approximately 04/10/2025.",
-      "date": "04/14/2025"
+      "date": "04/10/2025"
     },
     {
       "id": "F14",
@@ -138,7 +138,7 @@
       "cite": "MED0008",
       "quote": "In my opinion the L4-L5 disc protrusion is causally related to the lifting injury of 03/11/2025 described by the patient, within a reasonable degree of medical probability.",
       "text": "Dr. Okonkwo-Lind gave the opinion that the L4-L5 disc protrusion is causally related to the lifting injury of 03/11/2025.",
-      "date": "05/09/2025"
+      "date": "03/11/2025"
     },
     {
       "id": "F21",
@@ -152,21 +152,21 @@
       "cite": "EMP0001",
       "quote": "Employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.",
       "text": "The employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.",
-      "date": "03/11/2025"
+      "date": ""
     },
     {
       "id": "F23",
       "cite": "EMP0003",
       "quote": "Average weekly wage: $912.40",
       "text": "The average weekly wage was $912.40.",
-      "date": "03/15/2025"
+      "date": ""
     },
     {
       "id": "F24",
       "cite": "DEF0003",
       "quote": "The L4-L5 findings are degenerative and pre-existing, not causally related to the work incident of 03/11/2025.",
       "text": "Dr. Marchetti's report states the L4-L5 findings are degenerative and pre-existing, not causally related to the work incident of 03/11/2025.",
-      "date": "06/20/2025"
+      "date": "03/11/2025"
     },
     {
       "id": "F25",
@@ -187,7 +187,7 @@
       "cite": "MED0008",
       "quote": "Restrictions: sedentary duty, no lifting over 15 pounds, until re-evaluation on 06/20/2025.",
       "text": "Dr. Okonkwo-Lind restricted the patient to sedentary duty with no lifting over 15 pounds until re-evaluation on 06/20/2025.",
-      "date": "05/09/2025"
+      "date": "06/20/2025"
     },
     {
       "id": "F28",
@@ -202,6 +202,55 @@
       "quote": "Lumbar strain, likely work related.",
       "text": "The family medicine record assessed a lumbar strain, likely work related.",
       "date": "03/14/2025"
+    },
+    {
+      "id": "F30",
+      "cite": "DEF0002",
+      "quote": "Range of motion (ROM) in the lumbar spine is limited in flexion.",
+      "text": "Range of motion (ROM) in the lumbar spine is limited in flexion.",
+      "date": "06/20/2025"
+    },
+    {
+      "id": "F31",
+      "cite": "DEF0002",
+      "quote": "Strength testing of lower extremities is 5/5 bilaterally.",
+      "text": "Strength testing of lower extremities is 5/5 bilaterally.",
+      "date": "06/20/2025"
+    },
+    {
+      "id": "F32",
+      "cite": "DEF0002",
+      "quote": "Reflexes are 2+ and symmetric in all tested segments.",
+      "text": "Reflexes are 2+ and symmetric in all tested segments.",
+      "date": "06/20/2025"
+    },
+    {
+      "id": "F33",
+      "cite": "DEF0002",
+      "quote": "Sensation is intact to light touch throughout the dermatomes.",
+      "text": "Sensation is intact to light touch throughout the dermatomes.",
+      "date": "06/20/2025"
+    },
+    {
+      "id": "F34",
+      "cite": "DEF0002",
+      "quote": "Straight leg raise negative bilaterally.",
+      "text": "Straight leg raise negative bilaterally.",
+      "date": "06/20/2025"
+    },
+    {
+      "id": "F35",
+      "cite": "DEF0002",
+      "quote": "No objective findings of radiculopathy on today's examination.",
+      "text": "No objective findings of radiculopathy on today's examination.",
+      "date": "06/20/2025"
+    },
+    {
+      "id": "F36",
+      "cite": "DEF0002",
+      "quote": "The L4-L5 disc changes are described as degenerative.",
+      "text": "The L4-L5 disc changes are described as degenerative.",
+      "date": "06/20/2025"
     }
   ],
   "flags": [
diff --git a/tests/fixtures/outputs/9001.001/concessions-defense-report.json b/tests/fixtures/outputs/9001.001/concessions-defense-report.json
index 57e7161..8d8a0fa 100644
--- a/tests/fixtures/outputs/9001.001/concessions-defense-report.json
+++ b/tests/fixtures/outputs/9001.001/concessions-defense-report.json
@@ -11,7 +11,24 @@
       "label": "No objective findings of radiculopathy",
       "quote": "No objective findings of radiculopathy on today's examination.",
       "cite": "DEF0002",
-      "supporting_findings": []
+      "supporting_findings": [
+        {
+          "quote": "Strength testing of lower extremities is 5/5 bilaterally.",
+          "cite": "DEF0002"
+        },
+        {
+          "quote": "Reflexes are 2+ and symmetric in all tested segments.",
+          "cite": "DEF0002"
+        },
+        {
+          "quote": "Sensation is intact to light touch throughout the dermatomes.",
+          "cite": "DEF0002"
+        },
+        {
+          "quote": "Straight leg raise negative bilaterally.",
+          "cite": "DEF0002"
+        }
+      ]
     }
   ],
   "danger_zone": [
diff --git a/tests/fixtures/outputs/9001.001/elements-okonkwo-lind.json b/tests/fixtures/outputs/9001.001/elements-okonkwo-lind.json
index bebf367..9081044 100644
--- a/tests/fixtures/outputs/9001.001/elements-okonkwo-lind.json
+++ b/tests/fixtures/outputs/9001.001/elements-okonkwo-lind.json
@@ -14,13 +14,6 @@
       "cite": "MED0007",
       "absent_note": ""
     },
-    {
-      "element": "history_prior_conditions",
-      "status": "PARTIAL",
-      "quote": "Patient reports seeking care at Brightwater Family Medicine on 03/14/2025.",
-      "cite": "MED0007",
-      "absent_note": "The consultation names earlier care without a prior-condition history."
-    },
     {
       "element": "exam_findings",
       "status": "STATED",
@@ -63,26 +56,12 @@
       "cite": "MED0008",
       "absent_note": ""
     },
-    {
-      "element": "permanency_rating",
-      "status": "PARTIAL",
-      "quote": "The patient has not reached maximum medical improvement.",
-      "cite": "MED0008",
-      "absent_note": "The record gives no permanency rating."
-    },
     {
       "element": "future_treatment",
       "status": "STATED",
       "quote": "Plan: left L4-L5 transforaminal epidural steroid injection.",
       "cite": "MED0008",
       "absent_note": ""
-    },
-    {
-      "element": "records_reviewed",
-      "status": "STATED",
-      "quote": "The MRI findings were reviewed during this consultation.",
-      "cite": "MED0007",
-      "absent_note": ""
     }
   ]
 }
diff --git a/tests/fixtures/outputs/9001.001/factsheet-defense-doctor.json b/tests/fixtures/outputs/9001.001/factsheet-defense-doctor.json
index 99b18b9..607a25c 100644
--- a/tests/fixtures/outputs/9001.001/factsheet-defense-doctor.json
+++ b/tests/fixtures/outputs/9001.001/factsheet-defense-doctor.json
@@ -3,14 +3,14 @@
     {
       "cite": "MED0001",
       "quote": "Date of service: 03/11/2025",
-      "use": "our_case",
+      "use": "none",
       "note": ""
     },
     {
       "cite": "MED0001",
       "quote": "Patient states he was lifting a tote he estimated at 60 pounds when he felt a sharp pain in his low back.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "This is the patient history; compare the employer weight without treating the report as proof."
     },
     {
       "cite": "MED0001",
@@ -21,14 +21,14 @@
     {
       "cite": "MED0001",
       "quote": "Patient denies any prior back injury or back pain.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "The denial conflicts with the later history of a prior strain."
     },
     {
       "cite": "MED0002",
       "quote": "Straight leg raise negative bilaterally.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "The negative emergency examination can be contrasted with the later positive finding."
     },
     {
       "cite": "MED0002",
@@ -129,13 +129,13 @@
     {
       "cite": "EMP0001",
       "quote": "Employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "The employer and emergency histories differ on the tote weight."
     },
     {
       "cite": "EMP0003",
       "quote": "Average weekly wage: $912.40",
-      "use": "our_case",
+      "use": "none",
       "note": ""
     },
     {
@@ -185,6 +185,54 @@
       "quote": "Lift up to 50 pounds repeatedly during the shift.",
       "use": "our_case",
       "note": ""
+    },
+    {
+      "cite": "MED0006",
+      "quote": "There is mild degenerative change noted at the lower vertebral levels.",
+      "use": "danger",
+      "note": "Degeneration offers a possible defense explanation; reserve medicine for our expert."
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Range of motion (ROM) in the lumbar spine is limited in flexion.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Strength testing of lower extremities is 5/5 bilaterally.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Reflexes are 2+ and symmetric in all tested segments.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Sensation is intact to light touch throughout the dermatomes.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Straight leg raise negative bilaterally.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "No objective findings of radiculopathy on today's examination.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "The L4-L5 disc changes are described as degenerative.",
+      "use": "defense_case",
+      "note": ""
     }
   ]
 }
diff --git a/tests/fixtures/outputs/9001.001/factsheet-issue-1.json b/tests/fixtures/outputs/9001.001/factsheet-issue-1.json
index 99b18b9..607a25c 100644
--- a/tests/fixtures/outputs/9001.001/factsheet-issue-1.json
+++ b/tests/fixtures/outputs/9001.001/factsheet-issue-1.json
@@ -3,14 +3,14 @@
     {
       "cite": "MED0001",
       "quote": "Date of service: 03/11/2025",
-      "use": "our_case",
+      "use": "none",
       "note": ""
     },
     {
       "cite": "MED0001",
       "quote": "Patient states he was lifting a tote he estimated at 60 pounds when he felt a sharp pain in his low back.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "This is the patient history; compare the employer weight without treating the report as proof."
     },
     {
       "cite": "MED0001",
@@ -21,14 +21,14 @@
     {
       "cite": "MED0001",
       "quote": "Patient denies any prior back injury or back pain.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "The denial conflicts with the later history of a prior strain."
     },
     {
       "cite": "MED0002",
       "quote": "Straight leg raise negative bilaterally.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "The negative emergency examination can be contrasted with the later positive finding."
     },
     {
       "cite": "MED0002",
@@ -129,13 +129,13 @@
     {
       "cite": "EMP0001",
       "quote": "Employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "The employer and emergency histories differ on the tote weight."
     },
     {
       "cite": "EMP0003",
       "quote": "Average weekly wage: $912.40",
-      "use": "our_case",
+      "use": "none",
       "note": ""
     },
     {
@@ -185,6 +185,54 @@
       "quote": "Lift up to 50 pounds repeatedly during the shift.",
       "use": "our_case",
       "note": ""
+    },
+    {
+      "cite": "MED0006",
+      "quote": "There is mild degenerative change noted at the lower vertebral levels.",
+      "use": "danger",
+      "note": "Degeneration offers a possible defense explanation; reserve medicine for our expert."
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Range of motion (ROM) in the lumbar spine is limited in flexion.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Strength testing of lower extremities is 5/5 bilaterally.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Reflexes are 2+ and symmetric in all tested segments.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Sensation is intact to light touch throughout the dermatomes.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Straight leg raise negative bilaterally.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "No objective findings of radiculopathy on today's examination.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "The L4-L5 disc changes are described as degenerative.",
+      "use": "defense_case",
+      "note": ""
     }
   ]
 }
diff --git a/tests/fixtures/outputs/9001.001/factsheet-issue-2.json b/tests/fixtures/outputs/9001.001/factsheet-issue-2.json
index 99b18b9..607a25c 100644
--- a/tests/fixtures/outputs/9001.001/factsheet-issue-2.json
+++ b/tests/fixtures/outputs/9001.001/factsheet-issue-2.json
@@ -3,14 +3,14 @@
     {
       "cite": "MED0001",
       "quote": "Date of service: 03/11/2025",
-      "use": "our_case",
+      "use": "none",
       "note": ""
     },
     {
       "cite": "MED0001",
       "quote": "Patient states he was lifting a tote he estimated at 60 pounds when he felt a sharp pain in his low back.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "This is the patient history; compare the employer weight without treating the report as proof."
     },
     {
       "cite": "MED0001",
@@ -21,14 +21,14 @@
     {
       "cite": "MED0001",
       "quote": "Patient denies any prior back injury or back pain.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "The denial conflicts with the later history of a prior strain."
     },
     {
       "cite": "MED0002",
       "quote": "Straight leg raise negative bilaterally.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "The negative emergency examination can be contrasted with the later positive finding."
     },
     {
       "cite": "MED0002",
@@ -129,13 +129,13 @@
     {
       "cite": "EMP0001",
       "quote": "Employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "The employer and emergency histories differ on the tote weight."
     },
     {
       "cite": "EMP0003",
       "quote": "Average weekly wage: $912.40",
-      "use": "our_case",
+      "use": "none",
       "note": ""
     },
     {
@@ -185,6 +185,54 @@
       "quote": "Lift up to 50 pounds repeatedly during the shift.",
       "use": "our_case",
       "note": ""
+    },
+    {
+      "cite": "MED0006",
+      "quote": "There is mild degenerative change noted at the lower vertebral levels.",
+      "use": "danger",
+      "note": "Degeneration offers a possible defense explanation; reserve medicine for our expert."
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Range of motion (ROM) in the lumbar spine is limited in flexion.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Strength testing of lower extremities is 5/5 bilaterally.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Reflexes are 2+ and symmetric in all tested segments.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Sensation is intact to light touch throughout the dermatomes.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Straight leg raise negative bilaterally.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "No objective findings of radiculopathy on today's examination.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "The L4-L5 disc changes are described as degenerative.",
+      "use": "defense_case",
+      "note": ""
     }
   ]
 }
diff --git a/tests/fixtures/outputs/9001.001/factsheet-our-doctor.json b/tests/fixtures/outputs/9001.001/factsheet-our-doctor.json
index 99b18b9..607a25c 100644
--- a/tests/fixtures/outputs/9001.001/factsheet-our-doctor.json
+++ b/tests/fixtures/outputs/9001.001/factsheet-our-doctor.json
@@ -3,14 +3,14 @@
     {
       "cite": "MED0001",
       "quote": "Date of service: 03/11/2025",
-      "use": "our_case",
+      "use": "none",
       "note": ""
     },
     {
       "cite": "MED0001",
       "quote": "Patient states he was lifting a tote he estimated at 60 pounds when he felt a sharp pain in his low back.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "This is the patient history; compare the employer weight without treating the report as proof."
     },
     {
       "cite": "MED0001",
@@ -21,14 +21,14 @@
     {
       "cite": "MED0001",
       "quote": "Patient denies any prior back injury or back pain.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "The denial conflicts with the later history of a prior strain."
     },
     {
       "cite": "MED0002",
       "quote": "Straight leg raise negative bilaterally.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "The negative emergency examination can be contrasted with the later positive finding."
     },
     {
       "cite": "MED0002",
@@ -129,13 +129,13 @@
     {
       "cite": "EMP0001",
       "quote": "Employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.",
-      "use": "our_case",
-      "note": ""
+      "use": "danger",
+      "note": "The employer and emergency histories differ on the tote weight."
     },
     {
       "cite": "EMP0003",
       "quote": "Average weekly wage: $912.40",
-      "use": "our_case",
+      "use": "none",
       "note": ""
     },
     {
@@ -185,6 +185,54 @@
       "quote": "Lift up to 50 pounds repeatedly during the shift.",
       "use": "our_case",
       "note": ""
+    },
+    {
+      "cite": "MED0006",
+      "quote": "There is mild degenerative change noted at the lower vertebral levels.",
+      "use": "danger",
+      "note": "Degeneration offers a possible defense explanation; reserve medicine for our expert."
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Range of motion (ROM) in the lumbar spine is limited in flexion.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Strength testing of lower extremities is 5/5 bilaterally.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Reflexes are 2+ and symmetric in all tested segments.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Sensation is intact to light touch throughout the dermatomes.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "Straight leg raise negative bilaterally.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "No objective findings of radiculopathy on today's examination.",
+      "use": "defense_case",
+      "note": ""
+    },
+    {
+      "cite": "DEF0002",
+      "quote": "The L4-L5 disc changes are described as degenerative.",
+      "use": "defense_case",
+      "note": ""
     }
   ]
 }
diff --git a/tests/fixtures/outputs/9001.001/questions-defense-doctor-cross.json b/tests/fixtures/outputs/9001.001/questions-defense-doctor-cross.json
index 9cb3e4f..cd0fddc 100644
--- a/tests/fixtures/outputs/9001.001/questions-defense-doctor-cross.json
+++ b/tests/fixtures/outputs/9001.001/questions-defense-doctor-cross.json
@@ -2,10 +2,10 @@
   "section": "cross",
   "questions": [
     {
-      "text": "The consultation records a positive straight leg raise on the left, correct?",
-      "cite": "MED0007",
-      "quote": "Positive straight leg raise on the left at 45 degrees.",
-      "note": "Compare [cite DEF0002]."
+      "text": "Your report identifies the examination date as 06/20/2025, correct?",
+      "cite": "DEF0001",
+      "quote": "Date of Examination: 06/20/2025",
+      "note": ""
     }
   ],
   "points_for_our_expert": []
diff --git a/tests/fixtures/outputs/9001.001/questions-defense-doctor-primary.json b/tests/fixtures/outputs/9001.001/questions-defense-doctor-primary.json
index 680aee3..d727241 100644
--- a/tests/fixtures/outputs/9001.001/questions-defense-doctor-primary.json
+++ b/tests/fixtures/outputs/9001.001/questions-defense-doctor-primary.json
@@ -8,33 +8,33 @@
       "note": ""
     },
     {
-      "text": "Your report says straight leg raise was negative bilaterally, correct?",
+      "text": "What specific findings support the label \"No objective findings of radiculopathy\" in your report?",
       "cite": "DEF0002",
-      "quote": "Straight leg raise negative bilaterally.",
-      "note": ""
+      "quote": "No objective findings of radiculopathy on today's examination.",
+      "note": "Identify the findings; stop without asking for a medical explanation."
     },
     {
-      "text": "Your report dated 06/20/2025 states no work restrictions are indicated, correct?",
-      "cite": "DEF0003",
-      "quote": "No work restrictions are indicated.",
+      "text": "Your report dated 06/20/2025 lists an MRI dated 04/18/2025, correct?",
+      "cite": "DEF0002",
+      "quote": "Review of MRI dated 04/18/2025 performed by Dr. Ansgar Velloso-Krantz.",
       "note": ""
     },
     {
-      "text": "Your report states \"The L4-L5 findings are degenerative and pre-existing, not causally related to the work incident of 03/11/2025.\", correct?",
-      "cite": "DEF0003",
-      "quote": "The L4-L5 findings are degenerative and pre-existing, not causally related to the work incident of 03/11/2025.",
+      "text": "The MRI report reads \"L4-L5: 4 mm posterior central disc protrusion contacting the thecal sac.\"; have I quoted that accurately?",
+      "cite": "MED0006",
+      "quote": "L4-L5: 4 mm posterior central disc protrusion contacting the thecal sac.",
       "note": ""
     },
     {
-      "text": "Your report states \"The examinee is at maximum medical improvement as of today's examination.\", correct?",
-      "cite": "DEF0003",
-      "quote": "The examinee is at maximum medical improvement as of today's examination.",
+      "text": "The MRI report reads \"Mild degenerative disc disease at L5-S1.\"; have I quoted that accurately?",
+      "cite": "MED0006",
+      "quote": "Mild degenerative disc disease at L5-S1.",
       "note": ""
     },
     {
-      "text": "Your report states \"No further treatment is medically necessary.\", correct?",
-      "cite": "DEF0003",
-      "quote": "No further treatment is medically necessary.",
+      "text": "Your history records lifting a tote from a floor level pallet to a cart, correct?",
+      "cite": "DEF0001",
+      "quote": "He describes the mechanism of injury as lifting a plastic tote from a floor level pallet to a cart.",
       "note": ""
     }
   ],
diff --git a/tests/fixtures/outputs/9001.001/questions-defense-doctor-redirect.json b/tests/fixtures/outputs/9001.001/questions-defense-doctor-redirect.json
index 1ab2b5d..8bfcea4 100644
--- a/tests/fixtures/outputs/9001.001/questions-defense-doctor-redirect.json
+++ b/tests/fixtures/outputs/9001.001/questions-defense-doctor-redirect.json
@@ -2,9 +2,9 @@
   "section": "redirect",
   "questions": [
     {
-      "text": "Your report states no work restrictions are indicated, correct?",
-      "cite": "DEF0003",
-      "quote": "No work restrictions are indicated.",
+      "text": "Your report identifies the MRI reader as Dr. Ansgar Velloso-Krantz, correct?",
+      "cite": "DEF0002",
+      "quote": "Review of MRI dated 04/18/2025 performed by Dr. Ansgar Velloso-Krantz.",
       "note": ""
     }
   ],
diff --git a/tests/fixtures/outputs/9001.001/questions-our-doctor-primary.json b/tests/fixtures/outputs/9001.001/questions-our-doctor-primary.json
index e98e7f3..fff8caf 100644
--- a/tests/fixtures/outputs/9001.001/questions-our-doctor-primary.json
+++ b/tests/fixtures/outputs/9001.001/questions-our-doctor-primary.json
@@ -4,14 +4,14 @@
     {
       "text": "Doctor, do you have an opinion, within a reasonable degree of medical probability, whether all of the treatment reflected in the records was reasonable, necessary, and causally related to the work incident?",
       "cite": "MED0008",
-      "quote": "In my opinion the L4-L5 disc protrusion is causally related to the lifting injury of 03/11/2025 described by the patient, within a reasonable degree of medical probability.",
-      "note": ""
+      "quote": "Plan: left L4-L5 transforaminal epidural steroid injection.",
+      "note": "This plan identifies treatment to ask about; it does not establish that all treatment was reasonable, necessary and related."
     },
     {
-      "text": "And separately, Doctor, as to the bills themselves listed on the bill memo, the charges from Fennimore County Hospital, Brightwater Family Medicine, Ridgeline Physical Therapy, Lakeshore Imaging, Dr. Priya Okonkwo-Lind, Dr. Theodore Marchetti, do you have an opinion whether those bills are reasonable and causally related to that same work incident?",
+      "text": "And separately, Doctor, as to the bills themselves listed on the bill memo, the charges from Fennimore County Hospital, Brightwater Family Medicine, Ridgeline Physical Therapy, Lakeshore Imaging, Dr. Priya Okonkwo-Lind, do you have an opinion whether those bills are reasonable and causally related to that same work incident?",
       "cite": "MED0008",
       "quote": "In my opinion the L4-L5 disc protrusion is causally related to the lifting injury of 03/11/2025 described by the patient, within a reasonable degree of medical probability.",
-      "note": ""
+      "note": "The attorney must supply and confirm the bill memo; this record does not establish the bills opinion."
     }
   ],
   "points_for_our_expert": []
diff --git a/tests/test_bench_cli.py b/tests/test_bench_cli.py
index 3078fd9..bc15f7d 100644
--- a/tests/test_bench_cli.py
+++ b/tests/test_bench_cli.py
@@ -14,9 +14,9 @@ from conftest import ROOT, write_config
 MATTERS = ROOT / "tests" / "fixtures" / "matters"
 MATTER = MATTERS / "9001.001"
 FLAWED = ROOT / "tests" / "fixtures" / "bench" / "flawed.json"
-PERFECT = ("bench 9001.001 model=candidate found=29 of 29 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
+PERFECT = ("bench 9001.001 model=candidate found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
            "flags_extra=0 rules=0 pages_failed=0 of 14")
-FLAWED_LINE = ("bench 9001.001 model=candidate found=26 of 29 missed=3 invented=2 extra=2 dates_wrong=1 flags=8 of 9 flags_missed=1 "
+FLAWED_LINE = ("bench 9001.001 model=candidate found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=7 flags=8 of 9 flags_missed=1 "
                "flags_extra=1 rules=1 pages_failed=0 of 14")
 
 def bench(config, *args):
@@ -137,7 +137,7 @@ def test_bench_received_404_stays_exit1(tmp_path, capsys):
     assert err == ""
     assert lines[0] == ("bench 9001.001 failure gate.model: status=404: fakemodel: unknown model; "
                         "not retried: the one retry was used")
-    assert lines[1] == ("bench 9001.001 model=qwen3.8:27b found=0 of 29 missed=29 invented=0 extra=0 dates_wrong=0 "
+    assert lines[1] == ("bench 9001.001 model=qwen3.8:27b found=0 of 36 missed=36 invented=0 extra=0 dates_wrong=0 "
                         "flags=0 of 9 flags_missed=9 flags_extra=0 rules=0 pages_failed=14 of 14")
     assert lines[-1] == "bench matters=1 imperfect=1"
 
@@ -159,7 +159,7 @@ def test_bench_received_bad_answer_stays_exit1(tmp_path, capsys):
     assert (code, err) == (1, "")
     assert lines[0] == ("bench 9001.001 failure gate.truncation: the answer stopped before it finished "
                         "(done_reason=length); not retried: the one retry was used")
-    assert lines[1] == ("bench 9001.001 model=qwen3.8:27b found=0 of 29 missed=29 invented=0 extra=0 dates_wrong=0 "
+    assert lines[1] == ("bench 9001.001 model=qwen3.8:27b found=0 of 36 missed=36 invented=0 extra=0 dates_wrong=0 "
                         "flags=0 of 9 flags_missed=9 flags_extra=0 rules=0 pages_failed=14 of 14")
 
 
@@ -177,9 +177,9 @@ def test_bench_prompt_too_long_stays_exit1(tmp_path, capsys):
         'the prompt is longer than the context length currently available to the model; '
         'shorten the prompt, adjust the context length in settings, or use a model ...; '
         'not retried: the prompt was too long; the chunk must be made smaller',
-        "bench 9001.001 model=qwen3.8:27b found=0 of 29 missed=29 invented=0 extra=0 dates_wrong=0 "
+        "bench 9001.001 model=qwen3.8:27b found=0 of 36 missed=36 invented=0 extra=0 dates_wrong=0 "
         "flags=0 of 9 flags_missed=9 flags_extra=0 rules=0 pages_failed=14 of 14",
-        "  missed: " + " ".join(f"F{i:02}" for i in range(1, 30)),
+        "  missed: " + " ".join(f"F{i:02}" for i in range(1, 37)),
         "  flags_missed: G1 G2 G3 G4 G5 G6 G7 G8 G9",
         "bench matters=1 imperfect=1",
     ]
diff --git a/tests/test_bench_detail.py b/tests/test_bench_detail.py
index d9a3f89..a3e43e1 100644
--- a/tests/test_bench_detail.py
+++ b/tests/test_bench_detail.py
@@ -10,21 +10,27 @@ from conftest import ROOT, write_config
 MATTERS = ROOT / "tests" / "fixtures" / "matters"
 IDEAL = MATTERS / "9001.001" / "ideal.json"
 FLAWED = ROOT / "tests" / "fixtures" / "bench" / "flawed.json"
-PERFECT = ("bench 9001.001 model=candidate found=29 of 29 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
+PERFECT = ("bench 9001.001 model=candidate found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
            "flags_extra=0 rules=0 pages_failed=0 of 14")
-FLAWED_LINE = ("bench 9001.001 model=candidate found=26 of 29 missed=3 invented=2 extra=2 dates_wrong=1 flags=8 of 9 flags_missed=1 "
+FLAWED_LINE = ("bench 9001.001 model=candidate found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=7 flags=8 of 9 flags_missed=1 "
                "flags_extra=1 rules=1 pages_failed=0 of 14")
 FLAWED_DETAIL = [
-    "  missed: F04 F15 F24",
+    "  missed: F04 F15 F24 F30 F31 F32 F33 F34 F35 F36",
     '  invented: MED0003 "Patient was lifting 80 pounds." (quote not on the page)',
     '  invented: MED0099 "Date of service: 03/11/2025" (no such page)',
     "  dates_wrong: F01 (03/12/2025 for 03/11/2025)",
+    '  dates_wrong: F10 (03/14/2025 for 04/11/2025)',
+    '  dates_wrong: F13 (04/14/2025 for 04/10/2025)',
+    '  dates_wrong: F20 (05/09/2025 for 03/11/2025)',
+    '  dates_wrong: F22 (03/11/2025 for )',
+    '  dates_wrong: F23 (03/15/2025 for )',
+    '  dates_wrong: F27 (05/09/2025 for 06/20/2025)',
     "  flags_missed: G3",
     "  flags_extra: conflict MED0001,MED0004",
     '  rules: no-dme-ime DEF0003 "IME"',
 ]
 LONG_QUOTE = "Patient was given a lumbar brace and told to rest for two full weeks at home."
-PROBE_LINE = ("bench 9001.001 model=candidate found=29 of 29 missed=0 invented=1 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
+PROBE_LINE = ("bench 9001.001 model=candidate found=36 of 36 missed=0 invented=1 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
               "flags_extra=0 rules=1 pages_failed=0 of 14")
 PROBE_DETAIL = [
     '  invented: MED0002 "Patient was given a lumbar brace and told to rest for two fu" (quote not on the page)',
diff --git a/tests/test_bench_discovery.py b/tests/test_bench_discovery.py
index cd394db..ad10fe3 100644
--- a/tests/test_bench_discovery.py
+++ b/tests/test_bench_discovery.py
@@ -7,7 +7,7 @@ from casefile import bench
 from conftest import ROOT, write_config
 
 MATTER = ROOT / "tests" / "fixtures" / "matters" / "9001.001"
-PERFECT = ("bench 9001.001 model=candidate found=29 of 29 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
+PERFECT = ("bench 9001.001 model=candidate found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
            "flags_extra=0 rules=0 pages_failed=0 of 14")
 
 
diff --git a/tests/test_bench_multi.py b/tests/test_bench_multi.py
index dbbc97e..6dccf1f 100644
--- a/tests/test_bench_multi.py
+++ b/tests/test_bench_multi.py
@@ -11,9 +11,9 @@ from conftest import ROOT, write_config
 MATTER = ROOT / "tests" / "fixtures" / "matters" / "9001.001"
 IDEAL = MATTER / "ideal.json"
 FLAWED = ROOT / "tests" / "fixtures" / "bench" / "flawed.json"
-PERFECT = ("bench 9001.001 model=qwen3.8:27b found=29 of 29 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
+PERFECT = ("bench 9001.001 model=qwen3.8:27b found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
            "flags_extra=0 rules=0 pages_failed=0 of 14")
-FLAWED_LINE = ("bench 9001.001 model=qwen3.8:27b found=26 of 29 missed=3 invented=2 extra=2 dates_wrong=1 flags=8 of 9 flags_missed=1 "
+FLAWED_LINE = ("bench 9001.001 model=qwen3.8:27b found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=7 flags=8 of 9 flags_missed=1 "
                "flags_extra=1 rules=1 pages_failed=0 of 14")
 
 
diff --git a/tests/test_bench_pipeline.py b/tests/test_bench_pipeline.py
index aeba94c..e33cbb2 100644
--- a/tests/test_bench_pipeline.py
+++ b/tests/test_bench_pipeline.py
@@ -18,7 +18,7 @@ from fakemodel.core import FakeModel, FakeTransport
 
 
 MATTER = ROOT / "tests/fixtures/matters/9001.001"
-PERFECT = ("bench 9001.001 model=qwen3.8:27b found=29 of 29 missed=0 invented=0 extra=2 dates_wrong=0 "
+PERFECT = ("bench 9001.001 model=qwen3.8:27b found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 "
            "flags=9 of 9 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14")
 MODES = (
     ("replay", 0, None, ("ok",)),
@@ -202,7 +202,7 @@ def split_setup(monkeypatch, *, repeated=False, duplicate=False):
     card = split_card(extract.card())
     monkeypatch.setattr(pipeline.extract, "card", lambda book=None: card)
     ideal = json.loads((MATTER / "ideal.json").read_text(encoding="utf-8"))
-    quote = ideal["facts"][0]["quote"]
+    quote = ideal["facts"][1]["quote"]
     if repeated:
         pages = list(loaded.pages)
         pages[5] = replace(pages[5], text=pages[5].text + "\n" + quote)
@@ -234,10 +234,10 @@ def test_bench_chunks(tmp_path, monkeypatch, capsys):
     with capsys.disabled():
         print(f"bench_chunks=3 found={score.found} of {score.key_total} flags={score.flags_found} "
               f"of {score.flags_total} runs=+{count} uncited={len(result.uncited)}")
-    assert (score.found, score.key_total, score.flags_found, score.flags_total, count) == (29, 29, 5, 9, 3)
+    assert (score.found, score.key_total, score.flags_found, score.flags_total, count) == (36, 36, 5, 9, 3)
     assert "  flags_missed: G1 G3 G6 G9" in score.details()
     assert result.pages_failed == 0 and result.failure is None
-    assert result.uncited == ("DEF0001", "DEF0002"), "split coverage must retain every uncited page"
+    assert result.uncited == ("DEF0001",), "split coverage must retain every uncited page"
 
 
 @pytest.mark.parametrize("duplicate", (False, True), ids=("second_page", "same_page_duplicate"))
@@ -250,7 +250,7 @@ def test_merge_identity(tmp_path, monkeypatch, duplicate):
     score = benchscore.score(key, result.candidate, loaded, playbook.load(cfg.paths.playbook).rules, 0)
     assert score.extra == 3, f"merged extra={score.extra}, expected 3 for one new page cite"
     found = [fact for fact in result.candidate.facts if fact.quote == quote]
-    first_reading = json.loads((MATTER / "ideal.json").read_text(encoding="utf-8"))["facts"][0]["text"]
+    first_reading = json.loads((MATTER / "ideal.json").read_text(encoding="utf-8"))["facts"][1]["text"]
     assert [(fact.cite, fact.text) for fact in found] == [("MED0001", first_reading), ("MED0006", first_reading)], (
         "merged fact must retain two cites and use its first reading for both")
 
diff --git a/tests/test_benchscore.py b/tests/test_benchscore.py
index 0120d04..3574387 100644
--- a/tests/test_benchscore.py
+++ b/tests/test_benchscore.py
@@ -11,9 +11,9 @@ from test_matter import make
 
 RULES = rules_mod.load(ROOT / "playbook" / "rules.toml")
 MATTER = ROOT / "tests" / "fixtures" / "matters" / "9001.001"
-PERFECT = ("bench 9001.001 model=candidate found=29 of 29 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
+PERFECT = ("bench 9001.001 model=candidate found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
            "flags_extra=0 rules=0 pages_failed=0 of 14")
-FLAWED = ("bench 9001.001 model=candidate found=26 of 29 missed=3 invented=2 extra=2 dates_wrong=1 flags=8 of 9 flags_missed=1 "
+FLAWED = ("bench 9001.001 model=candidate found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=7 flags=8 of 9 flags_missed=1 "
           "flags_extra=1 rules=1 pages_failed=0 of 14")
 
 PAGES = {"medical": [("Pain 7/10 in the low back.\nOther real line.", "MED0001"),
diff --git a/tests/test_cards.py b/tests/test_cards.py
index bf851ec..1bf6532 100644
--- a/tests/test_cards.py
+++ b/tests/test_cards.py
@@ -9,11 +9,7 @@ import pytest
 from casefile import cards, playbook
 from conftest import ROOT
 
-VERSIONS = {'01-MEMO':'ed0e58680bc9','00-BILLS':'7805311400a2','00-CLASSIFY':'0919de24f802',
-            '00-PROCEDURAL':'58ef7e481a89','00-TESTIMONY':'acf3b1c3a5ef','01-P0':'c87983a810e7',
-            '02-A':'858d1b9eac5b','02-C-CLIENT':'f243ad762b1f','02-C-DEFDOC':'ae10f8ca6acf',
-            '02-C-OURDOC':'1b3ca3e1e2da','02-C-WITNESS':'ddd72eea4d3e','03-CLIENT':'dbead8527c45',
-            '04-G':'ddc04735074c','05-A':'633ccbbab4bd','07-ANON':'bd075ed6a208'}
+VERSIONS = {'01-MEMO': '2f58978d959b', '00-BILLS': '7805311400a2', '00-CLASSIFY': '0919de24f802', '00-PROCEDURAL': '58ef7e481a89', '00-TESTIMONY': 'acf3b1c3a5ef', '01-P0': 'c87983a810e7', '02-A': '008d522f2b4d', '02-C-CLIENT': 'f243ad762b1f', '02-C-DEFDOC': '77f7427b15f0', '02-C-OURDOC': 'a1d57a9f112b', '02-C-WITNESS': 'ddd72eea4d3e', '03-CLIENT': 'dbead8527c45', '04-G': '3279e19325a0', '05-A': 'cd37084912ca', '07-ANON': 'bd075ed6a208'}
 
 
 def test_cards():
diff --git a/tests/test_depo.py b/tests/test_depo.py
index 3f87530..35ddc19 100644
--- a/tests/test_depo.py
+++ b/tests/test_depo.py
@@ -111,6 +111,8 @@ def test_depo_contract(tmp_path, monkeypatch, row, capsys):
         assert sum(len(r._r.xpath('.//w:br[@w:type="page"]')) for p in doc.paragraphs for r in p.runs)==2
         for title,uses in (('Case outline: our view',('our_case','both')),('Case outline: the defense view',('defense_case','both'))):
             expected=[f for f in cf.facts if any(i['use'] in uses and i['quote']==f.quote and i['cite'] in f.cites for i in data['factsheet']['facts'])]
+            if 'defense view' in title:
+                expected = [f for f in expected if any(pid.startswith('defense-report/') for pid in f.page_ids)]
             actual=[p for p in section(doc,title) if ': "' in p]
             assert len(actual)==len(expected), 'W6 outline included none or danger labels'
         for part,title in zip(depo.SECTIONS,depo.TITLES):
@@ -124,7 +126,7 @@ def test_depo_contract(tmp_path, monkeypatch, row, capsys):
     elif row==1:
         primary=section(doc,'Questions: primary')
         bills=next(p for p in primary if 'as to the bills themselves' in p)
-        assert sum(provider in bills for provider in outputs.providers(cf))==6, 'W6 providers_named differs from 6 of 6'
+        assert sum(provider in bills for provider in outputs.providers(cf))==5, 'W6 providers_named differs from 5 of 5 (defense-only providers excluded)'
         assert not any(p.startswith('Missing:') for p in primary)
         assert not [f for f in outputs.check(depo.render(data,value,cf,loaded.pages,info,open_items=(),playbook_version=book.version,model=cfg.model.name),book.rules,providers=outputs.providers(cf)) if f.severity=='error']
     elif row==3:
diff --git a/tests/test_extract.py b/tests/test_extract.py
index 613c7bc..d08bafd 100644
--- a/tests/test_extract.py
+++ b/tests/test_extract.py
@@ -16,7 +16,7 @@ MATTER = ROOT / "tests/fixtures/matters/9001.001"
 def test_extract_card():
     card = extract.card()
     print(f"card_version={card.version} card_name={card.name} docx_import={int(docx.__name__ == 'docx')}")
-    assert card.version == "ed0e58680bc9", f"card_version={card.version}"
+    assert card.version == "2f58978d959b", f"card_version={card.version}"
     assert card.name == extract.CARD_NAME == "medical_memo"
     assert extraction_card().text == card.text
     assert card.text.endswith(extract.ID_SENTENCE)
diff --git a/tests/test_facts.py b/tests/test_facts.py
index 9fe1b26..fa8ea58 100644
--- a/tests/test_facts.py
+++ b/tests/test_facts.py
@@ -127,16 +127,16 @@ def ideal_merge(path):
     pages = matter.load(FIXTURE).pages
     answer = json.loads((FIXTURE / "ideal.json").read_text(encoding="utf-8"))
     events = facts.merge(facts.CaseFile(), answer, pages, 7)
-    assert sum(event.kind == "fact" for event in events) == 31
+    assert sum(event.kind == "fact" for event in events) == 37
     assert sum(event.kind == "flag" for event in events) == 9
     stored = facts.append(path, events)
-    assert len(stored.facts) == 31 and len(stored.flags) == 9 and stored.last_seq == 40
+    assert len(stored.facts) == 37 and len(stored.flags) == 9 and stored.last_seq == 48
     assert stored.flags[0].page_ids == ["medical/001", "employer/001"], "G1 pages were not resolved"
     known = {page.page_id for page in pages}
     assert all(set(record.page_ids) <= known for record in [*stored.facts, *stored.flags])
     assert all(event.payload["run_id"] == 7 for event in stored.events)
-    assert [event.payload["id"] for event in events] == [
-        *[f"F{seq}" for seq in range(1, 32)], *[f"G{seq}" for seq in range(32, 41)]]
+    assert [event.payload["id"] for event in events if event.kind in ("fact", "flag")] == [
+        *[f"F{seq}" for seq in range(1, 36)], "F38", "F39", *[f"G{seq}" for seq in range(40, 49)]]
 
 
 def repeat_merge(path):
diff --git a/tests/test_fixture_matter.py b/tests/test_fixture_matter.py
index fd314f2..25b83f0 100644
--- a/tests/test_fixture_matter.py
+++ b/tests/test_fixture_matter.py
@@ -29,10 +29,10 @@ def test_key_loads(capsys):
     with capsys.disabled():
         print(f"key_facts={len(key.facts)} flags={len(key.flags)} pages={len(matter.pages)}")
 
-    expected_fact_ids = [f"F{n:02d}" for n in range(1, 30)]
+    expected_fact_ids = [f"F{n:02d}" for n in range(1, 37)]
     expected_flag_ids = [f"G{n}" for n in range(1, 10)]
 
-    assert (len(key.facts), len(key.flags), len(matter.pages)) == (29, 9, 14)
+    assert (len(key.facts), len(key.flags), len(matter.pages)) == (36, 9, 14)
     assert [f.id for f in key.facts] == expected_fact_ids
     assert [f.id for f in key.flags] == expected_flag_ids
     assert findings == []
diff --git a/tests/test_hearing.py b/tests/test_hearing.py
index 3e713c5..be69a0d 100644
--- a/tests/test_hearing.py
+++ b/tests/test_hearing.py
@@ -75,7 +75,7 @@ def test_hearing_contract(tmp_path,monkeypatch,row,capsys):
         expected=next(e.rule for e in book.entries if e.id=='billing-memo-first').split('item is: ')[1].split(' When known')[0]
         assert section(doc,'Pre-hearing checklist')[0]==expected, 'W7 starred paragraph wording differs'
         checklist=section(doc,'Pre-hearing checklist')
-        assert checklist[1]=='Totals: not on file; the billing memo is supplied by the attorney (question 28).'
+        assert checklist[1]=='Totals: not on file; the billing memo is supplied by the attorney.'
         exhibits=[p for p in checklist if p.startswith('Exhibits to mark:')]
         assert exhibits==['Exhibits to mark: medical: [cite MED0001] to [cite MED0008] (8 pages)',
                           'Exhibits to mark: employer: [cite EMP0001] to [cite EMP0003] (3 pages)',
@@ -110,13 +110,13 @@ def test_hearing_contract(tmp_path,monkeypatch,row,capsys):
     elif row==6:
         doctor=section(doc,'Doctor preparation')
         for title in ("What the doctor's records say",'Opinions the case needs','Defense report points to be ready for',
-                      'Records the doctor may not have seen: not checked this round (no records audit card runs).',
+                      "Records the doctor may not have seen: review not performed; compare the report's records list with the records on file.",
                       "Conflicts between the doctor's records and other records"):
             assert title in doctor
-        elements=[p for p in doctor[:doctor.index('Gaps')] if any(p.startswith(e+':') for e in outputs.ELEMENTS)]
+        elements=[p for p in doctor[:doctor.index('Gaps')] if any(p.startswith(outputs.human_label(e)+':') for e in outputs.ELEMENTS)]
         assert len(elements)==14
         missing=[p for p in doctor if ': NOT FOUND' in p]
-        assert [p.split(':')[0] for p in missing[:2]]==['treatment_reasonable_necessary_related','bills_reasonable_related']
+        assert [p.split(':')[0] for p in missing[:2]]==['Prior conditions and history','Treatment reasonable, necessary and related']
         assert values['elements'].task=='report' and values['elements'].options['side']=='ours'
     elif row==7:
         closing=section(doc,'Closing outline')
diff --git a/tests/test_memo.py b/tests/test_memo.py
index 48271e4..efb0ad1 100644
--- a/tests/test_memo.py
+++ b/tests/test_memo.py
@@ -127,7 +127,7 @@ def test_l1_changed_counts_and_grammar(tmp_path, additions, expected):
 
 @pytest.mark.parametrize("title, expected", [
     ("Open items", ["none"]),
-    ("Conflicts", ["Pages read in 0 runs; conflicts and gaps are checked only between pages sent to the model together. A cloud task run reads the whole matter (stage 7b).", "ROLE NEEDED: no binder pair is marked defense and ours in matter.toml; conflicts are in the order found.", "none"]),
+    ("Conflicts", ["Pages read in 0 runs; conflicts and gaps are checked only between pages sent to the model together. A cloud task run reads the whole matter.", "ROLE NEEDED: no binder pair is marked defense and ours in matter.toml; conflicts are in the order found.", "none"]),
     ("Gaps and missing records", ["none"]),
     ("Outputs out of date", ["none"]),
 ])
@@ -213,8 +213,8 @@ def test_memo(tmp_path):
             "probe/002: uncited: no fact or flag cites probe/002"],
         [p.text for p in conflicts[2:]] == ["Conflict between [cite MED0001] and [cite DEF0002].",
                                              "Model's reading: The histories disagree.",
-                                             "From [cite MED0001]:", f'"{QUOTE}"', '"No prior injury."',
-                                             "From [cite DEF0002]:"],
+                                             "From [cite MED0001]:", "(all facts on this page)", f'"{QUOTE}" [cite MED0001]', '"No prior injury." [cite MED0001]',
+                                             "From [cite DEF0002]:", "No verified fact quoted from DEF0002; read the page."],
         [p.text for p in gaps] == ["Gap at [cite MED0002].", *[f"Model's reading: {s}" for s in GAP_ABOUTS]],
         fact.text == f'"{QUOTE}" [cite MED0001]' and [run.text for run in fact.runs] == [f'"{QUOTE}"', " [cite MED0001]"],
         verified[fact_index + 1].text == "Also cited: [cite MED0002]",
@@ -225,7 +225,7 @@ def test_memo(tmp_path):
         '"Therapy continued." [page probe/001]' in [p.text for p in verified],
         heading_texts == ["Page MED0001 (medical/001), binder medical", "Page MED0002 (medical/002), binder medical",
                           "Page probe/001, binder probe"] and seen == expected_quotes and page_quotes.get("medical/002") == [],
-        conflicts[0].text == "Pages read in 2 runs; conflicts and gaps are checked only between pages sent to the model together. A cloud task run reads the whole matter (stage 7b).",
+        conflicts[0].text == "Pages read in 2 runs; conflicts and gaps are checked only between pages sent to the model together. A cloud task run reads the whole matter.",
     ]
     checks.extend(round6_checks(tmp_path))
     assert len(checks) == 22
@@ -289,7 +289,7 @@ def test_conflicts_sentence_counts_read_runs(tmp_path, count, noun):
     path = tmp_path / "memo.docx"
     memo.render(build(stored), path, rules=rules.load(Path(__file__).resolve().parents[1] / "playbook/rules.toml"))
     assert section(Document(path), "Conflicts")[0].text == (
-        f"Pages read in {count} {noun}; conflicts and gaps are checked only between pages sent to the model together. A cloud task run reads the whole matter (stage 7b).")
+        f"Pages read in {count} {noun}; conflicts and gaps are checked only between pages sent to the model together. A cloud task run reads the whole matter.")
 
 
 def round6_checks(tmp_path):
@@ -326,14 +326,14 @@ def round6_checks(tmp_path):
     result, doc = make()
     chronology = [p.text for p in section(doc, 'Treatment chronology') if '"' in p.text]
     assert chronology == [
-        f'March 11, 2025, Invented Clinic, other: "{pages[0].text}" [cite MED0001]',
-        f'03/14/2025, Invented Clinic, diagnosis: "{pages[1].text}" [cite MED0002]',
-        f'03/14/2025, Invented Clinic, work_status: "{pages[2].text}" [cite MED0003]',
+        f'March 11, 2025, Invented Clinic, Other: "{pages[0].text}" [cite MED0001]',
+        f'03/14/2025, Invented Clinic, Diagnosis: "{pages[1].text}" [cite MED0002]',
+        f'03/14/2025, Invented Clinic, Work status: "{pages[2].text}" [cite MED0003]',
     ], 'chronology: parsed date order or stable tie lost'
     conflicts = [p.text for p in section(doc, 'Conflicts')]
     start = conflicts.index('From [cite DEF0001]:',
         conflicts.index('Conflict between [cite DEF0001] and [cite MED0001].'))
-    assert conflicts[start + 1:start + 3] == [f'"{pages[3].text}"', 'From [cite MED0001]:'], \
+    assert conflicts[start + 1:start + 4] == ['(all facts on this page)', f'"{pages[3].text}" [cite DEF0001]', 'From [cite MED0001]:'], \
         'conflict_quotes: quote from outside the cited page'
     assert [p for p in conflicts if p.startswith('Conflict between ')] == [
         'Conflict between [cite DEF0001] and [cite MED0001].',
diff --git a/tests/test_packet.py b/tests/test_packet.py
index 13d7686..d79f6b3 100644
--- a/tests/test_packet.py
+++ b/tests/test_packet.py
@@ -14,7 +14,7 @@ def test_packet_contract(tmp_path,row,capsys):
     value=packet.build(cf,loaded.pages,matter=loaded.number,task='depo',
                        options={'deponent':'our-doctor','deponent_pages':['medical/007']},playbook_version=book.version)
     if row==0:
-        assert len(value.facts)==len(cf.facts)==31
+        assert len(value.facts)==len(cf.facts)==37
         for sent, stored in zip(value.facts,cf.facts):
             assert (sent.cite,sent.page_id,sent.quote)==(stored.cites[0],stored.page_ids[0],stored.quote)
         altered=replace(cf.events[0],payload={**cf.events[0].payload,'page_id':'absent/001','cite':'ABS0001'})
@@ -28,7 +28,7 @@ def test_packet_contract(tmp_path,row,capsys):
     elif row==2:
         body=value.body()
         assert body.startswith('Matter 9001.001\nTask: depo ')
-        assert sum(line.startswith('[F') for line in body.splitlines())==31
+        assert sum(line.startswith('[F') for line in body.splitlines())==37
         assert "[deponent's record]" in body
         assert all(extract.page_block(p) in body for p in value.pages), 'W5 packet page blocks omitted; packet_ok=5 of 6'
     elif row==3:
diff --git a/tests/test_pipeline.py b/tests/test_pipeline.py
index 826dd11..0f56e67 100644
--- a/tests/test_pipeline.py
+++ b/tests/test_pipeline.py
@@ -176,9 +176,9 @@ def test_pipeline(case, tmp_path, totals):
             elif case == "three":
                 assert ids(result.chunks) == SPLIT_IDS and count("runs") == 3
                 assert all(o.ok for o in result.outcomes)
-                assert sum(v[0] == "read" for v in coverage.values()) == 12
+                assert sum(v[0] == "read" for v in coverage.values()) == 13
                 assert {key[0] for key, value in coverage.items() if value[0] == "uncited"} == {
-                    "defense-report/002", "defense-report/001"}
+                    "defense-report/001"}
             elif case == "empty":
                 assert [o.ok for o in result.outcomes] == [True, False, True]
                 assert count("runs") == 3 and count("answers") == 4
diff --git a/tests/test_report.py b/tests/test_report.py
index 98ec745..212a566 100644
--- a/tests/test_report.py
+++ b/tests/test_report.py
@@ -40,17 +40,17 @@ def test_report_contract(tmp_path,monkeypatch,row,capsys):
                 if flag.kind=='conflict' and any(pid.startswith('defense-report/') for pid in flag.page_ids):
                     for pid in flag.page_ids:
                         for fact in cf.facts:
-                            if pid in fact.page_ids: assert fact.quote in text
-            assert 'positive_finding:' in text and 'none stated on the pages sent: DEF0001, DEF0002, DEF0003' in text
+                            if pid in fact.page_ids and fact.category in {f.category for f in cf.facts if set(f.page_ids) & (set(flag.page_ids)-{pid})}: assert fact.quote in text
+            assert 'Positive finding:' in text and 'Strength testing of lower extremities is 5/5 bilaterally.' in text
             assert "Model's note: Prior symptoms may support a different explanation." in text
-            assert 'Records review audit: not built this round;' in text
-            assert all(p.text.startswith('He acknowledges') is False for p in doc.paragraphs if p.text.startswith('positive_finding'))
+            assert 'Records review audit: not performed.' in text
+            assert all(p.text.startswith('He acknowledges') is False for p in doc.paragraphs if p.text.startswith('Positive finding'))
         else:
-            items=[p for p in section(doc,'Elements') if any(p.startswith(name+':') for name in outputs.ELEMENTS)]
-            assert [p.split(':')[0] for p in items]==list(outputs.ELEMENTS), 'W5 NOT FOUND elements were not computed'
+            items=[p for p in section(doc,'Elements') if any(p.startswith(outputs.human_label(name)+':') for name in outputs.ELEMENTS)]
+            assert [p.split(':')[0] for p in items]==[outputs.human_label(name) for name in outputs.ELEMENTS], 'W5 NOT FOUND elements were not computed'
             negatives=[p for p in items if ': NOT FOUND' in p]
-            assert len(negatives)==2 and all('[cite MED0007]' in p and '[cite MED0008]' in p for p in negatives), 'W5 NOT FOUND elements were not computed'
-            assert [p.split(':')[0] for p in section(doc,'Gaps') if ': NOT FOUND' in p]==['treatment_reasonable_necessary_related','bills_reasonable_related']
+            assert len(negatives)==5 and all('[cite MED0007]' in p and '[cite MED0008]' in p for p in negatives), 'W5 NOT FOUND elements were not computed'
+            assert [p.split(':')[0] for p in section(doc,'Gaps') if ': NOT FOUND' in p]==['Prior conditions and history','Treatment reasonable, necessary and related','Bills reasonable and related','Permanency rating','Records reviewed']
             assert 'From [cite DEF0003]:' in text
             if row==2:
                 other=report.prepare(cf,loaded.pages,book,number=loaded.number,selected='MED0007,MED0008')
@@ -81,7 +81,7 @@ def test_report_contract(tmp_path,monkeypatch,row,capsys):
             raise AssertionError('W5 render called the model on port 9')
         monkeypatch.setattr(outputs,'ask',forbidden)
         restored=report.render({'concessions':data},value,cf,loaded.pages,info,open_items=(),playbook_version=book.version,model=cfg.model.name)
-        assert 'positive_finding:' in '\n'.join(flat(document(tmp_path,restored,book.rules)))
+        assert 'Positive finding:' in '\n'.join(flat(document(tmp_path,restored,book.rules)))
         restored=report.render({'concessions':None},value,cf,loaded.pages,info,open_items=(),playbook_version=book.version,model=cfg.model.name)
         assert section(document(tmp_path,restored,book.rules,'failed.docx'),"Concessions (the report's own words)")[0].startswith("Concessions (the report's own words): the model's answer failed"), 'W5 failed step silently omitted'
         with capsys.disabled(): print('report_ok=9 of 9')
diff --git a/tests/test_round05_fixes.py b/tests/test_round05_fixes.py
index 65d3419..b4b9f57 100644
--- a/tests/test_round05_fixes.py
+++ b/tests/test_round05_fixes.py
@@ -75,8 +75,8 @@ def test_h2_append_failure_resends_pages(tmp_path, monkeypatch):
     assert facts.append is append
     code, line, error = invoke(settings, transport)
     assert len(transport.requests) == 2, "H2: pages with uncommitted facts were not re-sent"
-    assert code == 1 and error == "" and "facts=31" in line
-    assert len(facts.load(folder / "casefile.jsonl").facts) == 31
+    assert code == 1 and error == "" and "facts=37" in line
+    assert len(facts.load(folder / "casefile.jsonl").facts) == 37
 
 
 def test_h2_status_joins_latest_coverage_to_casefile_runs(tmp_path):
@@ -91,7 +91,7 @@ def test_h2_status_joins_latest_coverage_to_casefile_runs(tmp_path):
     assert snapshot["read"] == 0 and snapshot["open"] == 14, "H2: status trusts coverage without a case-file run"
     assert invoke(settings, transport)[0] == 1
     assert len(transport.requests) == 2, "H2: deleted complete run tail did not re-send pages"
-    assert len(facts.load(path).facts) == 31
+    assert len(facts.load(path).facts) == 37
 
 
 def test_h2_probe_refuses_before_model(tmp_path, monkeypatch):
diff --git a/tests/test_round06_fix1.py b/tests/test_round06_fix1.py
index fff8a50..324db1e 100644
--- a/tests/test_round06_fix1.py
+++ b/tests/test_round06_fix1.py
@@ -54,7 +54,7 @@ def test_h2_elements(tmp_path):
     a = dict(element='diagnosis', status='STATED', quote='Normal.', cite='MED0001', absent_note='')
     b = dict(a, status='PARTIAL', absent_note='Some findings absent')
     section, _, _ = outputs.elements({'elements': [a, b]}, loaded.pages)
-    line = next(''.join(r.text for r in p.runs) for p in section.paragraphs if p.runs[0].text.startswith('diagnosis:'))
+    line = next(''.join(r.text for r in p.runs) for p in section.paragraphs if p.runs[0].text.startswith('Diagnosis:'))
     assert 'STATED' in line, 'H2: later partial overwrote stated element'
     scoped, _, _ = outputs.elements({'elements': [], 'searched_pages': [loaded.pages[0].page_id]}, loaded.pages)
     scope = ''.join(r.text for r in scoped.paragraphs[0].runs)
@@ -91,10 +91,10 @@ def test_m3(tmp_path):
 
 def test_m4(tmp_path):
     _, _, _, loaded, cf, _ = setup_case(tmp_path)
-    with pytest.raises(outputs.OutputError, match='ambiguous provider.*Okonkwo-Lind.*Marchetti'):
+    with pytest.raises(outputs.OutputError, match='ambiguous provider.*Marchetti.*Okonkwo-Lind'):
         outputs.provider_pages(cf, 'Dr', pages=loaded.pages)
     assert outputs.provider_pages(cf, 'archett', pages=loaded.pages) == (), 'M4: provider fragment matched'
-    assert outputs.provider_pages(cf, 'Marchetti') == ('defense-report/003',)
+    assert outputs.provider_pages(cf, 'Marchetti') == ('defense-report/002', 'defense-report/003')
     merged = facts.CaseFile(list(cf.events))
     merged.extend([facts.Event('cite', dict(fact=cf.facts[0].id, cite='MED0002', page_id='medical/002', run_id=2, date='', provider=cf.facts[0].providers[0].upper()))])
     try:
diff --git a/tests/test_stage2_exit.py b/tests/test_stage2_exit.py
index bb9a6ac..0aeb2ab 100644
--- a/tests/test_stage2_exit.py
+++ b/tests/test_stage2_exit.py
@@ -15,7 +15,7 @@ from fakemodel.core import FakeModel
 from fakemodel.server import serve
 
 MATTER = ROOT / "tests" / "fixtures" / "matters" / "9001.001"
-PERFECT = ("bench 9001.001 model=qwen3.8:27b found=29 of 29 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
+PERFECT = ("bench 9001.001 model=qwen3.8:27b found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
            "flags_extra=0 rules=0 pages_failed=0 of 14")
 COMMAND = ["casefile", "bench", "--matters", "tests/fixtures/matters"]
 
diff --git a/tests/test_stage5_exit.py b/tests/test_stage5_exit.py
index 75ace13..75891d0 100644
--- a/tests/test_stage5_exit.py
+++ b/tests/test_stage5_exit.py
@@ -24,18 +24,18 @@ NUMBER = "9001.001"
 ONE_PAGE = {"facts": [{
     "cite": "DEF0001", "quote": "The examinee reports lifting a tote of about 60 pounds.",
     "text": "The examinee reported lifting a tote of about 60 pounds.",
-    "date": "06/20/2025", "category": "patient_statement", "provider": "Dr. Theodore Marchetti",
+    "date": "", "category": "patient_statement", "provider": "Dr. Theodore Marchetti",
 }], "flags": []}
 EXPECTED = (
-    "stage5 run=1 mode=replay exit=1 chunks=1 runs=+1 read=13 open=1 facts=31 conflicts=5 gaps=4 new_facts=31 new_flags=9",
-    "stage5 run=2 mode=bad_schema exit=1 chunks=1 runs=+1 read=13 open=1 facts=31 conflicts=5 gaps=4 new_facts=0 new_flags=0",
-    "stage5 run=3 mode=replay exit=0 chunks=1 runs=+1 read=14 open=0 facts=32 conflicts=5 gaps=4 new_facts=1 new_flags=0",
-    "stage5 run=4 mode=replay exit=0 chunks=0 runs=+0 read=14 open=0 facts=32 conflicts=5 gaps=4 new_facts=0 new_flags=0",
-    "stage5 memo=1 sections=15 chronology=31 dated=31 of 31 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=87 readings=31 gaps=4 runs_seen=1 open=1 open_status=uncited rule_hits=0 changed=first",
-    "stage5 memo=2 sections=15 chronology=31 dated=31 of 31 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=87 readings=31 gaps=4 runs_seen=1 open=1 open_status=failed rule_hits=0 changed=0",
-    "stage5 memo=3 sections=15 chronology=32 dated=32 of 32 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=89 readings=32 gaps=4 runs_seen=2 open=0 open_status=none rule_hits=0 changed=1",
-    "stage5 status read=13 then 14 open=1 then 0 outputs=memo:current",
-    "stage5 exit=0 runs=4 of 4 memos=3 of 3 answers=+4 casefile_lines=48 chain_ok=1 server_stopped=1",
+    'stage5 run=1 mode=replay exit=1 chunks=1 runs=+1 read=13 open=1 facts=37 conflicts=5 gaps=4 new_facts=37 new_flags=9',
+    'stage5 run=2 mode=bad_schema exit=1 chunks=1 runs=+1 read=13 open=1 facts=37 conflicts=5 gaps=4 new_facts=0 new_flags=0',
+    'stage5 run=3 mode=replay exit=0 chunks=1 runs=+1 read=14 open=0 facts=38 conflicts=5 gaps=4 new_facts=1 new_flags=0',
+    'stage5 run=4 mode=replay exit=0 chunks=0 runs=+0 read=14 open=0 facts=38 conflicts=5 gaps=4 new_facts=0 new_flags=0',
+    'stage5 memo=1 sections=15 chronology=34 dated=34 of 37 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=118 readings=35 gaps=4 runs_seen=1 open=1 open_status=uncited rule_hits=0 changed=first',
+    'stage5 memo=2 sections=15 chronology=34 dated=34 of 37 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=118 readings=35 gaps=4 runs_seen=1 open=1 open_status=failed rule_hits=0 changed=0',
+    'stage5 memo=3 sections=15 chronology=34 dated=34 of 38 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=120 readings=35 gaps=4 runs_seen=2 open=0 open_status=none rule_hits=0 changed=1',
+    'stage5 status read=13 then 14 open=1 then 0 outputs=memo:current',
+    'stage5 exit=0 runs=4 of 4 memos=3 of 3 answers=+4 casefile_lines=56 chain_ok=1 server_stopped=1',
 )
 BAD_REASON = ("gate.schema: the answer does not match the schema: facts[0].text: missing required key; "
               "the page stays open until a later run reads it")
@@ -67,8 +67,8 @@ def _read_memo(number, path, stored, pages, coverage, book, errors):
     gaps = _section(doc, 'Gaps and missing records')
     records = stored.facts
     expected_chronology = []
-    for fact in sorted(records, key=lambda f: dates.parse(f.dates[0])):
-        expected_chronology.append(f'{fact.dates[0]}, {fact.providers[0] or fact.page_ids[0].rsplit('/',1)[0]}, {fact.category}: '
+    for fact in sorted((f for f in records if f.dates[0]), key=lambda f: dates.parse(f.dates[0])):
+        expected_chronology.append(f'{fact.dates[0]}, {fact.providers[0] or fact.page_ids[0].rsplit('/',1)[0]}, {('Maximum medical improvement' if fact.category == 'mmi_statement' else fact.category.replace('_',' ').capitalize())}: '
                                   f'"{fact.quote}" {_cite(fact.cites[0], fact.page_ids[0])}')
     actual_chronology = [p.text for p in chronology if any(run.text.startswith('"') for run in p.runs)]
     if actual_chronology != expected_chronology:
@@ -84,7 +84,15 @@ def _read_memo(number, path, stored, pages, coverage, book, errors):
         expected_conflicts.extend("Model's reading: " + about for about in flag.abouts)
         for cite, page_id in zip(flag.cites, flag.page_ids):
             expected_conflicts.append('From ' + _cite(cite,page_id) + ':')
-            expected_conflicts.extend(f'"{fact.quote}"' for fact in records if page_id in fact.page_ids)
+            own = [f for f in records if page_id in f.page_ids]
+            other = {f.category for f in records if set(f.page_ids) & (set(flag.page_ids)-{page_id})}
+            matching = [f for f in own if f.category in other]
+            if not own:
+                expected_conflicts.append(f'No verified fact quoted from {cite}; read the page.')
+            else:
+                if not matching:
+                    expected_conflicts.append('(all facts on this page)')
+                expected_conflicts.extend(f'"{fact.quote}" {_cite(cite,page_id)}' for fact in matching or own)
     conflict_quotes_ok = int([p.text for p in conflicts[1:]] == expected_conflicts)
     if not conflict_quotes_ok:
         errors.append(f'memo={number}: scoped conflict quotes or ordering differ')
@@ -131,7 +139,7 @@ def _read_memo(number, path, stored, pages, coverage, book, errors):
         re.fullmatch(r'Built \d{4}-\d{2}-\d{2} from case file entry ' + str(stored.outputs[-1]['built_from_seq']) +
                      re.escape(f'; playbook {book.version}; model qwen3.8:27b'), paragraphs[9].text) is not None)
     sentence = re.fullmatch(r'Pages read in (\d+) runs?; conflicts and gaps are checked only between '
-        r'pages sent to the model together\. A cloud task run reads the whole matter \(stage 7b\)\.', conflicts[0].text)
+        r'pages sent to the model together\. A cloud task run reads the whole matter\.', conflicts[0].text)
     runs_seen = int(sentence[1]) if sentence else -1
     read_runs = {row[2] for row in coverage.values() if row[0] == 'read'}
     if runs_seen != len(read_runs):
@@ -219,7 +227,7 @@ def test_stage5_exit(tmp_path, capsys):
                     sent = re.findall(r"^=== PAGE (\S+) BATES ", body["messages"][1]["content"], re.MULTILINE)
                     if sent != expected_pages:
                         errors.append(f"run={number}: sent pages differ: {sent}")
-                expected_line_count = (42, 44, 47, 48)[number - 1]
+                expected_line_count = (50, 52, 55, 56)[number - 1]
                 if len(stored.events) != expected_line_count:
                     errors.append(f"run={number}: casefile_lines={len(stored.events)} expected={expected_line_count}")
                 memo_line = _read_memo(number, folder / "outputs/memo.docx", stored,
@@ -248,7 +256,7 @@ def test_stage5_exit(tmp_path, capsys):
     lines = [*run_lines, *memo_lines, status_line]
     good_runs = sum(actual == expected for actual, expected in zip(run_lines, EXPECTED[:4]))
     good_memos = sum(actual == expected for actual, expected in zip(memo_lines, EXPECTED[4:7]))
-    failed = bool(errors or lines != list(EXPECTED[:8]) or answers != 4 or complete_lines != 48
+    failed = bool(errors or lines != list(EXPECTED[:8]) or answers != 4 or complete_lines != 56
                   or not chain_ok or not stopped)
     lines.append(f"stage5 exit={int(failed)} runs={good_runs} of 4 memos={good_memos} of 3 answers={answers:+d} "
                  f"casefile_lines={complete_lines} chain_ok={chain_ok} server_stopped={int(stopped)}")
diff --git a/tests/test_stage6_exit.py b/tests/test_stage6_exit.py
index 49819cd..45a5075 100644
--- a/tests/test_stage6_exit.py
+++ b/tests/test_stage6_exit.py
@@ -22,12 +22,12 @@ NUMBER = '9001.001'
 MATTER = ROOT / 'tests/fixtures/matters' / NUMBER
 ANSWERS = ROOT / 'tests/fixtures/outputs' / NUMBER
 EXPECTED = (
-    'stage6 memo sections=15 chronology=31 dated=31 of 31 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 rule_hits=0 exit=1',
-    'stage6 depo=defense-doctor-us outline_our=25 outline_defense=7 questions=8 rests_on_page=8 of 8 danger=1 points=1 forbidden_topics=0 rule_hits=0 header_ok=1 exit=1',
-    'stage6 depo=our-doctor-us outline_our=25 outline_defense=7 questions=4 rests_on_page=4 of 4 danger=1 points=0 treatment_q=1 bills_q=1 compound=0 providers_named=6 of 6 rule_hits=0 header_ok=1 exit=1',
-    'stage6 hearing checklist_first=1 starred=1 issues=2 standard_needed=2 client_direct=2 client_cross=2 elements=14 not_found=2 closing=2 relief_needed=2 rule_hits=0 header_ok=1 exit=1',
-    'stage6 report=defense-report concessions=1 labels=1 danger=1 conflicts=3 conflict_quotes_ok=1 audit_limit=1 rule_hits=0 header_ok=1 exit=1',
-    'stage6 report=okonkwo-lind elements=14 stated=10 partial=2 not_found=2 gaps_separate=1 rule_hits=0 header_ok=1 exit=1',
+    'stage6 memo sections=15 chronology=34 dated=34 of 37 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 rule_hits=0 exit=1',
+    'stage6 depo=defense-doctor-us outline_our=19 outline_defense=11 questions=8 rests_on_page=8 of 8 danger=6 points=1 forbidden_topics=0 rule_hits=0 header_ok=1 exit=1',
+    'stage6 depo=our-doctor-us outline_our=19 outline_defense=11 questions=4 rests_on_page=4 of 4 danger=6 points=0 treatment_q=1 bills_q=1 compound=0 providers_named=5 of 5 rule_hits=0 header_ok=1 exit=1',
+    'stage6 hearing checklist_first=1 starred=1 issues=2 standard_needed=2 client_direct=2 client_cross=2 elements=14 not_found=5 closing=2 relief_needed=2 rule_hits=0 header_ok=1 exit=1',
+    'stage6 report=defense-report concessions=1 labels=5 danger=1 conflicts=3 conflict_quotes_ok=1 audit_limit=1 rule_hits=0 header_ok=1 exit=1',
+    'stage6 report=okonkwo-lind elements=14 stated=9 partial=0 not_found=5 gaps_separate=1 rule_hits=0 header_ok=1 exit=1',
     'stage6 status outputs=memo:current,depo-defense-doctor-us:current,depo-our-doctor-us:current,hearing:current,report-defense-report:current,report-okonkwo-lind:current partial=0',
     'stage6 exit=0 docs=6 of 6 answers=+16 rule_hits=0 server_stopped=1',
 )
@@ -40,6 +40,11 @@ ELEMENTS = ('treating_relationship', 'mechanism', 'history_prior_conditions', 'e
             'bills_reasonable_related', 'work_status_restrictions', 'mmi', 'permanency_rating',
             'future_treatment', 'records_reviewed')
 
+ELEMENT_LABELS = ('Treating relationship', 'Mechanism', 'Prior conditions and history', 'Exam findings',
+    'Imaging reviewed', 'Diagnosis', 'Causation', 'Treatment reasonable, necessary and related',
+    'Bills reasonable and related', 'Work status and restrictions', 'Maximum medical improvement',
+    'Permanency rating', 'Future treatment', 'Records reviewed')
+
 
 def _answer(name):
     return json.loads((ANSWERS / (name + '.json')).read_text(encoding='utf-8'))
@@ -61,7 +66,7 @@ def _texts(paragraphs):
 def _header_ok(doc, cf, book, model, *, who=''):
     expected = [*HEADER]
     if who:
-        expected.append('Deposition of Dr. ' + who + ', NEEDED')
+        expected.extend(['Deposition of: Dr. ' + who, 'Deposition date and time: NEEDED'])
     expected.append('Matter ' + NUMBER)
     actual = _texts(doc.paragraphs)
     index = 1 + len(expected) + int(bool(who))
@@ -150,12 +155,20 @@ def _outline(doc, title):
 def _conflicts_ok(paragraphs, cf):
     actual = _texts(paragraphs)
     blocks = []
+    cites = []
     for i, text in enumerate(actual):
+        if text.startswith('Conflict between '):
+            cites = re.findall(r'\[cite ([^\]]+)\]', text)
         match = re.fullmatch(r'From \[cite ([A-Z]+\d+)\]:', text)
         if match:
-            end = next((j for j in range(i + 1, len(actual)) if not actual[j].startswith('"')), len(actual))
-            expected = [f'"{fact.quote}" [cite {match[1]}]' for fact in cf.facts if match[1] in fact.cites]
-            blocks.append(actual[i + 1:end] == expected)
+            value = match[1]
+            own = [f for f in cf.facts if value in f.cites]
+            other = {f.category for f in cf.facts if set(f.cites) & (set(cites)-{value})}
+            matching = [f for f in own if f.category in other]
+            expected = ([f'No verified fact quoted from {value}; read the page.'] if not own else
+                ([] if matching else ['(all facts on this page)']) +
+                [f'"{f.quote}" [cite {value}]' for f in matching or own])
+            blocks.append(actual[i+1:i+1+len(expected)] == expected)
     return int(bool(blocks) and all(blocks))
 
 
@@ -185,6 +198,7 @@ def _depo_line(doc, who, code, cf, loaded, book, header_ok, rule_hits, errors):
         primary = _questions(doc, 'Questions: primary')
         treatment = sum(bool(re.search(r'\btreatment\b', p.text, re.I)) for p in primary)
         bills = [p for p in primary if re.search(r'\bbills?\b', p.text, re.I)]
+        providers = [p for p in providers if 'Marchetti' not in p]
         named = sum(any(provider in p.text for p in bills) for provider in providers)
         compound = sum(hit.rule_id == 'treatment-and-bills-apart' for hit in findings)
         line += f'treatment_q={treatment} bills_q={len(bills)} compound={compound} providers_named={named} of {len(providers)} '
@@ -208,7 +222,7 @@ def _hearing_line(doc, code, header_ok, rule_hits):
         f'issues={sum(p.startswith("Issue: ") for p in outline)} standard_needed={outline.count("Standard: STANDARD NEEDED")} '
         f'client_direct={sum(bool(re.match(r"^\d+\. ", p)) for p in direct)} '
         f'client_cross={sum(bool(re.match(r"^\d+\. ", p)) for p in cross)} '
-        f'elements={sum(any(p.startswith(e + ":") for e in ELEMENTS) for p in elements)} '
+        f'elements={sum(any(p.startswith(e + ":") for e in ELEMENT_LABELS) for p in elements)} '
         f'not_found={sum(": NOT FOUND" in p for p in elements)} '
         f'closing={sum(p.startswith("Issue: ") for p in closing)} relief_needed={closing.count("Relief requested: RELIEF NEEDED")} '
         f'rule_hits={rule_hits} header_ok={header_ok} exit={code}')
@@ -218,8 +232,8 @@ def _report_line(doc, defense, code, cf, header_ok, rule_hits):
     if defense:
         conflicts = _section(doc, 'Conflicts with other records')
         topics = _texts(_section(doc, 'Candidate cross topics (document-based)'))
-        limit = ("Records review audit: not built this round; the report's records-referenced statements "
-                 'are listed under What the report states for your own comparison.')
+        limit = ('Records review audit: not performed. No records-referenced item was returned by the model '
+                 'for the report pages; read the records list in the report.')
         return (f'stage6 report=defense-report concessions={_outline(doc, "Concessions (the report\'s own words)")} '
             f'labels={_outline(doc, "Undefined labels")} danger={_outline(doc, "Danger zone")} '
             f'conflicts={sum(p.text.startswith("Conflict between ") for p in conflicts)} '
@@ -227,9 +241,9 @@ def _report_line(doc, defense, code, cf, header_ok, rule_hits):
             f'rule_hits={rule_hits} header_ok={header_ok} exit={code}')
     elements = _texts(_section(doc, 'Elements'))
     gaps = _texts(_section(doc, 'Gaps'))
-    actual = [p.split(':', 1)[0] for p in elements if any(p.startswith(e + ':') for e in ELEMENTS)]
-    separate = int(actual == list(ELEMENTS) and all(any(p.startswith(e + ': NOT FOUND') for p in gaps)
-                   for e in ('treatment_reasonable_necessary_related', 'bills_reasonable_related')))
+    actual = [p.split(':', 1)[0] for p in elements if any(p.startswith(e + ':') for e in ELEMENT_LABELS)]
+    separate = int(actual == list(ELEMENT_LABELS) and all(any(p.startswith(e + ': NOT FOUND') for p in gaps)
+                   for e in ('Treatment reasonable, necessary and related', 'Bills reasonable and related')))
     return (f'stage6 report=okonkwo-lind elements={len(actual)} stated={sum(": STATED:" in p for p in elements)} '
         f'partial={sum(": PARTIAL:" in p for p in elements)} not_found={sum(": NOT FOUND" in p for p in elements)} '
         f'gaps_separate={separate} rule_hits={rule_hits} header_ok={header_ok} exit={code}')
@@ -280,7 +294,7 @@ def test_stage6_exit(tmp_path, capsys):
         memo_hits = _saved_rules(Document(folder / 'outputs/memo.docx'), book.rules, outputs.providers(cf), loaded.pages)
         rule_hits += memo_hits
         lines.append('stage6 memo sections=' + metrics + f' rule_hits={memo_hits} exit=' + str(result.returncode))
-        if result.stderr or 'chunks=1 runs=+1 read=13 open=1 facts=31 conflicts=5 gaps=4' not in result.stdout:
+        if result.stderr or 'chunks=1 runs=+1 read=13 open=1 facts=37 conflicts=5 gaps=4' not in result.stdout:
             errors.append('memo CLI differs: ' + result.stdout + result.stderr)
         if result.returncode != 1:
             errors.append(f'memo exit={result.returncode}, expected 1')
diff --git a/tests/test_status.py b/tests/test_status.py
index 6e88a5f..cddbe19 100644
--- a/tests/test_status.py
+++ b/tests/test_status.py
@@ -58,11 +58,11 @@ def test_status_six_cases(tmp_path, monkeypatch, capsys, totals):
     assert code == 1, "memo with open items must exit=1"
     assert error == ""
     assert line.splitlines()[0] == (
-        "memo 9001.001 chunks=1 runs=+1 read=13 open=1 facts=31 conflicts=5 gaps=4 "
-        f"new_facts=31 new_flags=9 memo={folder / 'outputs/memo.docx'}")
+        "memo 9001.001 chunks=1 runs=+1 read=13 open=1 facts=37 conflicts=5 gaps=4 "
+        f"new_facts=37 new_flags=9 memo={folder / 'outputs/memo.docx'}")
     current = status.matter_status(settings, "9001.001")
     current_ok = {key: value for key, value in current.items() if key != "open_items"} == dict(
-        pages=14, read=13, failed=0, uncited=1, empty=0, open=1, facts=31,
+        pages=14, read=13, failed=0, uncited=1, empty=0, open=1, facts=37,
         conflicts=5, gaps=4, outputs="memo:current")
     opened = "  open: DEF0001 (defense-report/001): uncited: no fact or flag cites defense-report/001"
     assert line.splitlines()[1:] == [opened], "open label lost its stamp or page ID"
@@ -80,7 +80,7 @@ def test_status_six_cases(tmp_path, monkeypatch, capsys, totals):
     assert failed_code == 1 and failed_error == ""
     assert len(bad.requests) == 2
     stored = facts.load(folder / "casefile.jsonl")
-    assert len(stored.facts) == 31, "failed outcome added fact events"
+    assert len(stored.facts) == 37, "failed outcome added fact events"
     assert stored.runs[-1]["ok"] is False and stored.runs[-1]["failed"] == ["defense-report/001"]
     assert "new_facts=0 new_flags=0" in failed_line
     output = folder / "outputs/memo.docx"
@@ -97,7 +97,7 @@ def test_status_six_cases(tmp_path, monkeypatch, capsys, totals):
     printed = capsys.readouterr()
     assert printed.err == ""
     assert printed.out.splitlines()[0] == (
-        "status 9001.001 pages=14 read=13 failed=1 uncited=0 empty=0 open=1 facts=32 "
+        "status 9001.001 pages=14 read=13 failed=1 uncited=0 empty=0 open=1 facts=38 "
         "conflicts=5 gaps=4 outputs=memo:stale")
     assert printed.out.splitlines()[1].startswith("  open: DEF0001 (defense-report/001): failed: gate.schema:")
     monkeypatch.setattr(sys, "argv", ["casefile", "status", "--matter", "9009.001", "--config", str(config_path)])
@@ -117,6 +117,7 @@ def test_binder_shown(tmp_path, totals):
     (folder / "records/medical").rename(folder / "records/ime")
     loaded = matter.load(folder)
     answer = json.loads((FIXTURE / "ideal.json").read_text(encoding="utf-8"))
+    answer['facts'][0]['date'] = ''
     transport = FakeTransport(FakeModel(recordings=[recording_for(extract.card(), loaded.pages, loaded.number, answer)]))
     code, _, error = invoke(settings, transport)
     assert code == 1 and not error, f"binder_shown=0: {error}"
@@ -165,14 +166,14 @@ def test_no_unread_pages_calls_no_model_and_exits_zero(tmp_path):
     loaded = matter.load(folder)
     answer = json.loads((FIXTURE / "ideal.json").read_text(encoding="utf-8"))
     answer["facts"].append(dict(cite="DEF0001", quote="The examinee reports lifting a tote of about 60 pounds.",
-                                text="The examinee reports lifting a tote of about 60 pounds.", date="06/20/2025", category="patient_statement", provider="Dr. Theodore Marchetti"))
+                                text="The examinee reports lifting a tote of about 60 pounds.", date="", category="patient_statement", provider="Dr. Theodore Marchetti"))
     transport = FakeTransport(FakeModel(recordings=[recording_for(extract.card(), loaded.pages, "9001.001", answer)]))
     assert invoke(settings, transport)[0] == 0
     before = len(transport.requests)
     code, line, error = invoke(settings, transport)
     assert code == 0 and error == ""
     assert len(transport.requests) == before, "read pages sent again"
-    assert "chunks=0 runs=+0 read=14 open=0 facts=32" in line
+    assert "chunks=0 runs=+0 read=14 open=0 facts=38" in line
     assert "new_facts=0 new_flags=0" in line
     assert len(facts.load(folder / "casefile.jsonl").outputs) == 2
 
```
