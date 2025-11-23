# Human Review System - Complete Guide

## Overview

The human review system now supports **per-question scoring** with **AI comparison** and **automatic averaging**. Reviewers can see each candidate's answer alongside the AI score and provide their own assessment.

---

## 🎯 Key Features

### 1. **Per-Question Scoring**
- Score each of the 10 questions individually (0-100)
- See the candidate's full answer for each question
- View AI score beside each answer
- Automatic average calculation of AI + Human scores

### 2. **Flexible Scoring Methods**
You can choose how to score:

**Option A: Question-by-Question** (Recommended)
- More granular and detailed
- Direct comparison with AI scoring
- Better audit trail

**Option B: Category-Level**
- Score by category (Technical, Sales, Communication, etc.)
- Faster for experienced reviewers
- Overrides question-level scores if provided

### 3. **AI Comparison**
- See AI score for each question
- Compare your assessment with AI
- Average automatically calculated
- Track score differences

---

## 📋 How to Review a Candidate

### Step 1: Open Human Review Form

1. Go to **Assessment > Human Reviews**
2. Click **Create** or open existing review
3. Select the **Candidate**

### Step 2: Review Each Question

Go to the **"Question-by-Question Review"** tab:

```
┌─────────────────────────────────────────────────────────┐
│ Q1: Describe a time you automated a repetitive process │
├─────────────────────────────────────────────────────────┤
│ Answer:                                                 │
│ [Candidate's answer shown here in gray box]            │
│                                                         │
│ Scoring:                                                │
│ AI Score:        75 / 100  (badge)                     │
│ Your Score:      [_____] (input field)                 │
│ Average Score:   [█████░░░░░] 0/100 (progress bar)    │
└─────────────────────────────────────────────────────────┘
```

### Step 3: Score Each Answer

For each question:
1. Read the candidate's answer
2. Check the AI score (shown as blue badge)
3. Enter your score (0-100) based on:
   - Quality of answer
   - Depth of explanation
   - Relevance to question
   - Examples provided
   - Communication clarity

4. The **Average Score** updates automatically:
   - Formula: `(AI Score + Human Score) / 2`
   - Example: AI=75, Human=85 → Average=80

### Step 4: Add Overall Assessment

Go to **"Overall Assessment"** tab:
- **Strengths**: Key strengths you observed
- **Concerns**: Any red flags or concerns
- **Reviewer Notes**: Additional observations

### Step 5: Make Recommendation

Select your recommendation from the header:
- ❌ **Reject** - Not suitable for role
- ⚠️ **Reconsider** - Has potential but concerns exist
- ✅ **Interview** - Recommend moving to interview
- ⭐ **Strong Hire** - Excellent candidate

### Step 6: Save Review

Click **Save** - the system will:
- ✅ Calculate final overall score
- ✅ Update candidate status to "Reviewed"
- ✅ Create audit log entry
- ✅ Send notification if score differs significantly from AI

---

## 📊 Scoring Logic

### Question-Level Scoring

When you score by question, the system:

1. **For each question:**
   ```
   Average = (AI Score + Human Score) / 2
   ```

2. **Overall score:**
   ```
   Overall = Average of all 10 question scores
   ```

### Category-Level Scoring

If you use the **"Category Scores"** tab instead:

```
Overall = (Technical × 0.25) +
          (Sales × 0.25) +
          (Communication × 0.20) +
          (Learning × 0.15) +
          (Cultural Fit × 0.15)
```

**Note:** Category scores **override** question-level scores if both are provided.

---

## 🎨 Form Layout

### Tab 1: Question-by-Question Review
```
┌────────────────────────────────────────────┐
│ Instructions (blue info box)               │
├────────────────────────────────────────────┤
│ Q1: [Question text]                        │
│   Answer: [Gray box with candidate answer] │
│   AI Score: 75/100                         │
│   Your Score: [input]                      │
│   Average: [progress bar]                  │
├────────────────────────────────────────────┤
│ Q2: [Question text]                        │
│   ...                                      │
├────────────────────────────────────────────┤
│ ... (Q3-Q10)                               │
└────────────────────────────────────────────┘
```

### Tab 2: Category Scores (Optional)
```
┌────────────────────────────────────────┐
│ Warning: Category scores override     │
│ question-level scores                  │
├────────────────────────────────────────┤
│ Technical Score:      [progress bar]   │
│ Sales Score:          [progress bar]   │
│ Communication Score:  [progress bar]   │
│ Learning Score:       [progress bar]   │
│ Cultural Fit Score:   [progress bar]   │
└────────────────────────────────────────┘
```

### Tab 3: Overall Assessment
```
┌────────────────────────────────────────┐
│ Strengths:                             │
│ [text area]                            │
│                                        │
│ Concerns:                              │
│ [text area]                            │
│                                        │
│ Reviewer Notes:                        │
│ [text area]                            │
└────────────────────────────────────────┘
```

### Tab 4: Score Comparison
```
┌────────────────────────────────────────┐
│ AI Score:         [████████░░] 82/100  │
│ Human Score:      [█████████░] 87/100  │
│ Difference:       +5 points             │
│                                        │
│ Reason for Adjustment:                 │
│ [text area - shown if difference ≠ 0] │
└────────────────────────────────────────┘
```

---

## 💡 Best Practices

### 1. **Read All Answers First**
- Get a holistic view of the candidate
- Understand their communication style
- Look for patterns and consistency

### 2. **Consider AI Score as Baseline**
- AI provides objective language analysis
- You provide human judgment and context
- Both perspectives create balanced assessment

### 3. **Document Score Differences**
- If your score differs significantly from AI (±10 points)
- Explain why in "Reason for Adjustment"
- Helps improve AI model over time

### 4. **Use Strengths & Concerns**
- Specific examples from answers
- 3-5 bullet points each
- Focus on observable evidence

### 5. **Be Consistent**
- Use same criteria for all candidates
- Review multiple candidates in one session
- Compare similar experience levels

---

## 🔍 Example Review Workflow

### Candidate: John Doe
**Question 1**: "Describe a time you automated a process"

**Candidate's Answer:**
> "I automated our invoice processing using Python and built a script that reduced processing time from 4 hours to 15 minutes. Used pandas for data processing and integrated with QuickBooks API."

**Your Assessment:**
- ✅ Specific example with metrics (4 hours → 15 minutes)
- ✅ Technical details (Python, pandas, API)
- ✅ Business impact clear
- ❌ Could have mentioned challenges/learnings

**Scoring:**
- AI Score: 78/100 (good technical depth)
- Your Score: 82/100 (strong specific example)
- **Average: 80/100** ✅

### Overall After 10 Questions:
```
Q1 Average:  80/100
Q2 Average:  75/100
Q3 Average:  85/100
Q4 Average:  70/100
Q5 Average:  82/100
Q6 Average:  88/100
Q7 Average:  79/100
Q8 Average:  84/100
Q9 Average:  81/100
Q10 Average: 77/100

Overall Score: 80.1/100
Recommendation: Interview ✅
```

---

## 🚀 What Happens After Review

When you save a human review:

1. ✅ **Candidate Status** updated to "Reviewed"
2. ✅ **Overall Score** recalculated (now uses human review score)
3. ✅ **Ranking** updated if recommendation is positive
4. ✅ **Audit Log** created with reviewer details
5. ✅ **Notification** sent if score differs significantly from AI
6. ✅ **Candidate sees** updated status (if they have portal access)

---

## 📈 Score Comparison Examples

### Example 1: Agreement
```
Question 3: "How to handle unclear client requirements?"

AI Score:     85/100
Human Score:  83/100
Average:      84/100

Status: ✅ Close agreement - both recognize strong answer
```

### Example 2: Human Adjustment Up
```
Question 6: "Handling price objections"

AI Score:     72/100
Human Score:  88/100
Average:      80/100

Reason: "Candidate showed deep understanding of value selling
that AI may have missed. Real-world examples were exceptional."

Status: ⬆️ Human recognized quality AI undervalued
```

### Example 3: Human Adjustment Down
```
Question 9: "Saying no professionally"

AI Score:     81/100
Human Score:  68/100
Average:      74.5/100

Reason: "Answer was generic and lacked specific examples.
AI scored language quality but missed lack of practical depth."

Status: ⬇️ Human caught superficial answer
```

---

## 🛠️ Troubleshooting

### Q: I don't see candidate answers
**A:** Ensure candidate has submitted assessment and has `response_id` linked

### Q: AI scores showing 0
**A:** AI scoring may not have run yet. Check candidate status is "ai_scored"

### Q: Average not calculating
**A:** Must enter both AI score exists and human score > 0

### Q: Can't save review without category scores
**A:** This is now optional! Just score questions and add recommendation.

### Q: Which method should I use?
**A:** For detailed review: use question-by-question. For quick review: use category scores.

---

## 📝 Database Fields Reference

### Human Review Model Fields

**Per-Question Human Scores:**
- `q1_human_score` through `q10_human_score` (Float, 0-100)

**Per-Question Averages (Computed):**
- `q1_avg_score` through `q10_avg_score` (Float, computed, stored)

**Category Scores (Optional):**
- `technical_score`
- `sales_score`
- `communication_score`
- `learning_score`
- `cultural_fit_score`

**Overall:**
- `overall_score` (Computed from category OR question averages)
- `score_difference` (Human - AI difference)
- `ai_score_before` (Related field from candidate.ai_score_id)

---

## 🎓 Training Tips

### For New Reviewers:

1. **Start with Question-by-Question**
   - More guided process
   - See what AI evaluated
   - Learn scoring calibration

2. **Review Sample Candidates**
   - Compare your scores with experienced reviewers
   - Discuss differences
   - Calibrate expectations

3. **Use AI as Learning Tool**
   - When AI scores high, understand why
   - When AI scores low, look for red flags
   - Build your evaluation skills

### For Experienced Reviewers:

1. **Use Category Scores for Speed**
   - Faster workflow
   - Still review answers
   - Skip granular scoring

2. **Focus on Differentiators**
   - What makes candidate stand out?
   - Red flags AI might miss?
   - Cultural fit assessment

3. **Document Insights**
   - Help improve AI model
   - Share patterns with team
   - Build knowledge base

---

## 📊 Success Metrics

Track these to ensure quality reviews:

- ✅ Average review completion time
- ✅ Score variance between AI and human
- ✅ Inter-reviewer agreement
- ✅ Candidate outcome correlation
- ✅ Review notes quality

---

## 🔐 Security & Privacy

- ✅ Only assessment managers can create reviews
- ✅ Reviewer identity tracked in audit log
- ✅ All changes logged with timestamp
- ✅ Candidates see final scores only, not individual reviews
- ✅ Email notifications for significant score changes

---

**Last Updated:** 2025-11-15
**Version:** 17.0.2.0.0
**Module:** scholarix_assessment

For questions or support, contact the development team.
