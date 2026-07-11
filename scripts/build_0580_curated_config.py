#!/usr/bin/env python3
"""Materialise the explicitly curated Gate 1C skill configuration."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'internal-content/0580/syllabus'; TAX=BASE/'taxonomy'; CONFIG=ROOT/'config'

# Explicit per-point decomposition. There is deliberately no title-derived fallback.
COMMON={
'1.1':'identify-natural-numbers identify-integers identify-prime-numbers identify-square-numbers identify-cube-numbers find-common-factors find-common-multiples classify-rational-and-irrational-numbers find-reciprocals',
'1.2':'use-set-language-and-notation represent-sets-with-venn-diagrams calculate-number-of-set-elements apply-set-union apply-set-intersection apply-set-complement',
'1.3':'calculate-squares calculate-square-roots calculate-cubes calculate-cube-roots calculate-integer-powers calculate-roots-of-numbers',
'1.4':'recognise-proper-fractions recognise-improper-fractions recognise-mixed-numbers simplify-fractions convert-between-improper-fractions-and-mixed-numbers convert-fractions-to-decimals convert-decimals-to-fractions convert-between-fractions-and-percentages convert-between-decimals-and-percentages',
'1.5':'order-quantities-by-magnitude compare-quantities-using-equality-symbols compare-quantities-using-inequality-symbols',
'1.6':'calculate-with-integers calculate-with-fractions calculate-with-decimals apply-order-of-operations apply-brackets-in-calculations calculate-with-negative-numbers',
'1.7':'interpret-positive-integer-indices interpret-zero-indices interpret-negative-integer-indices apply-product-rule-for-indices apply-quotient-rule-for-indices apply-power-of-power-rule',
'1.8':'represent-numbers-in-standard-form convert-numbers-to-standard-form convert-numbers-from-standard-form calculate-with-standard-form',
'1.9':'round-to-decimal-places round-to-significant-figures estimate-calculation-results choose-appropriate-answer-accuracy',
'1.10':'find-lower-bound-of-rounded-value find-upper-bound-of-rounded-value',
'1.11':'simplify-ratios divide-quantity-in-given-ratio apply-ratio-in-context apply-direct-proportion',
'1.12':'calculate-rate-of-pay calculate-currency-exchange calculate-flow-rate calculate-density calculate-pressure calculate-population-density calculate-average-speed convert-compound-units',
'1.13':'calculate-percentage-of-quantity express-quantity-as-percentage calculate-percentage-increase calculate-percentage-decrease calculate-simple-interest calculate-compound-interest calculate-profit-and-loss calculate-discount',
'1.14':'use-calculator-efficiently enter-values-into-calculator interpret-calculator-display preserve-calculation-precision',
'1.15':'convert-units-of-time calculate-time-intervals use-twelve-hour-clock use-twenty-four-hour-clock read-timetables solve-time-zone-problems',
'1.16':'calculate-with-money convert-between-currencies',
'2.1':'represent-generalised-numbers-with-letters substitute-values-into-expressions substitute-values-into-formulas',
'2.2':'collect-like-terms expand-single-bracket expand-product-of-two-brackets factorise-by-common-factor',
'2.4':'interpret-algebraic-indices apply-algebraic-index-laws solve-simple-exponential-equations',
'2.5':'construct-algebraic-expressions construct-equations construct-formulas solve-linear-equation solve-simultaneous-linear-equations change-subject-of-formula',
'2.6':'represent-inequality-on-number-line interpret-inequality-on-number-line solve-linear-inequality',
'2.7':'continue-number-sequence recognise-sequence-pattern find-nth-term-of-linear-sequence find-nth-term-of-quadratic-sequence find-nth-term-of-cubic-sequence',
'2.9':'interpret-practical-graphs interpret-gradient-as-rate-of-change draw-graph-from-data interpret-distance-time-graph draw-distance-time-graph',
'2.10':'construct-table-of-values plot-graph-of-function interpret-graph-of-function solve-equations-graphically interpret-roots-from-graph draw-exponential-growth-graph draw-exponential-decay-graph',
'2.11':'sketch-linear-function sketch-quadratic-function sketch-cubic-function sketch-reciprocal-function',
'3.1':'read-cartesian-coordinates plot-cartesian-coordinates',
'3.2':'draw-linear-graph-from-equation',
'3.3':'calculate-gradient-from-graph',
'3.5':'interpret-gradient-intercept-form find-equation-of-line-from-graph',
'3.6':'identify-parallel-lines use-equal-gradients-for-parallel-lines',
'4.1':'use-geometric-vocabulary classify-triangles classify-quadrilaterals identify-lines-of-symmetry identify-rotational-symmetry',
'4.2':'construct-triangle-with-ruler-and-compasses construct-perpendicular-bisector construct-angle-bisector construct-perpendicular-line construct-locus',
'4.3':'interpret-scale-drawing construct-scale-drawing calculate-actual-length-from-scale',
'4.4':'identify-similar-shapes calculate-missing-lengths-in-similar-shapes',
'4.5':'identify-line-symmetry identify-order-of-rotational-symmetry',
'4.6':'interpret-three-letter-angle-notation apply-angles-around-a-point apply-angles-on-a-straight-line apply-vertically-opposite-angles apply-angle-sum-of-triangle apply-angle-sum-of-quadrilateral apply-corresponding-angles apply-alternate-angles apply-cointerior-angles calculate-interior-angle-of-regular-polygon calculate-exterior-angle-of-regular-polygon',
'4.7':'apply-angle-in-semicircle-theorem apply-tangent-radius-angle-property',
'5.1':'convert-metric-units-of-length convert-metric-units-of-area convert-metric-units-of-volume',
'5.2':'calculate-perimeter-of-polygon calculate-area-of-rectangle calculate-area-of-triangle calculate-area-of-parallelogram calculate-area-of-trapezium',
'5.3':'calculate-circumference-of-circle calculate-area-of-circle calculate-arc-length calculate-sector-area',
'5.4':'calculate-surface-area-of-prism calculate-volume-of-prism calculate-surface-area-of-cylinder calculate-volume-of-cylinder',
'5.5':'calculate-area-of-compound-shape calculate-perimeter-of-compound-shape calculate-volume-of-compound-solid calculate-surface-area-of-compound-solid',
'6.1':'apply-pythagoras-theorem find-missing-side-using-pythagoras',
'6.2':'use-sine-ratio use-cosine-ratio use-tangent-ratio find-side-in-right-triangle find-angle-in-right-triangle solve-angle-of-elevation solve-angle-of-depression solve-bearing-with-trigonometry',
'7.1':'reflect-shape rotate-shape translate-shape enlarge-shape describe-reflection describe-rotation describe-translation describe-enlargement',
'8.1':'calculate-single-event-probability use-probability-scale identify-impossible-event identify-certain-event calculate-complementary-probability',
'8.2':'calculate-relative-frequency calculate-expected-frequency compare-relative-frequency-with-theoretical-probability',
'8.3':'calculate-probability-of-combined-events construct-sample-space-diagram calculate-probability-of-mutually-exclusive-events calculate-probability-of-independent-events construct-probability-tree-diagram',
'9.1':'classify-categorical-data classify-discrete-data classify-continuous-data',
'9.2':'interpret-frequency-table construct-frequency-table identify-biased-data-collection evaluate-sampling-method',
'9.3':'calculate-mean calculate-median calculate-mode calculate-range choose-appropriate-average',
'9.4':'draw-bar-chart interpret-bar-chart draw-pie-chart interpret-pie-chart draw-pictogram interpret-pictogram',
'9.5':'draw-scatter-diagram identify-correlation draw-line-of-best-fit use-line-of-best-fit identify-unreliable-extrapolation',
}
EXT={
'1.10':'find-bounds-of-calculation-result','1.11':'apply-inverse-proportion','1.13':'calculate-reverse-percentage','1.17':'model-exponential-growth model-exponential-decay calculate-compound-growth calculate-compound-decay','1.18':'simplify-surds rationalise-denominator calculate-with-surds',
'2.2':'factorise-quadratic-expression factorise-difference-of-two-squares complete-square expand-multiple-algebraic-factors','2.3':'simplify-algebraic-fractions calculate-with-algebraic-fractions','2.5':'solve-equation-with-algebraic-fractions solve-quadratic-equation-by-factorisation solve-quadratic-equation-using-formula complete-square-to-solve-quadratic solve-simultaneous-linear-and-quadratic-equations change-subject-in-complex-formula','2.6':'solve-quadratic-inequality','2.7':'find-nth-term-of-exponential-sequence','2.8':'form-direct-proportion-equation form-inverse-proportion-equation solve-direct-proportion-problem solve-inverse-proportion-problem','2.9':'interpret-speed-time-graph draw-speed-time-graph calculate-distance-from-speed-time-graph calculate-acceleration-from-speed-time-graph','2.12':'differentiate-power-function find-gradient-using-derivative find-stationary-point classify-stationary-point','2.13':'use-function-notation evaluate-function find-inverse-function form-composite-function evaluate-composite-function',
'3.3':'calculate-gradient-from-two-points','3.4':'calculate-distance-between-two-points calculate-midpoint-of-line-segment','3.5':'find-equation-of-line-from-two-points find-equation-of-line-from-point-and-gradient','3.7':'identify-perpendicular-lines use-negative-reciprocal-gradients',
'4.4':'prove-shapes-similar identify-congruent-shapes prove-triangles-congruent calculate-area-scale-factor calculate-volume-scale-factor','4.5':'use-symmetry-properties-of-circle','4.6':'calculate-angle-sum-of-polygon calculate-interior-angle-of-irregular-polygon','4.7':'apply-centre-circumference-angle-theorem apply-same-segment-angle-theorem apply-cyclic-quadrilateral-angle-property apply-alternate-segment-theorem','4.8':'apply-tangent-chord-theorem apply-intersecting-chords-theorem apply-secant-tangent-theorem',
'5.2':'calculate-area-of-kite calculate-area-of-rhombus','5.4':'calculate-volume-of-pyramid calculate-surface-area-of-pyramid calculate-volume-of-cone calculate-surface-area-of-cone calculate-volume-of-sphere calculate-surface-area-of-sphere','5.5':'calculate-similar-area-ratio calculate-similar-volume-ratio',
'6.3':'recall-exact-sine-values recall-exact-cosine-values recall-exact-tangent-values','6.4':'interpret-trigonometric-function-graph solve-trigonometric-equation-from-graph','6.5':'use-sine-rule use-cosine-rule calculate-triangle-area-using-sine solve-ambiguous-sine-rule-case','6.6':'solve-three-dimensional-pythagoras-problem solve-three-dimensional-trigonometry-problem',
'7.1':'enlarge-shape-with-negative-scale-factor enlarge-shape-with-fractional-scale-factor','7.2':'represent-vector-in-column-form add-vectors subtract-vectors multiply-vector-by-scalar use-position-vectors','7.3':'calculate-vector-magnitude','7.4':'solve-vector-geometry-problem prove-collinearity-using-vectors prove-parallel-lines-using-vectors',
'8.3':'calculate-probability-using-venn-diagram use-set-notation-in-probability','8.4':'calculate-conditional-probability apply-conditional-probability-to-tree-diagram',
'9.2':'design-questionnaire identify-sampling-bias','9.3':'calculate-quartiles calculate-interquartile-range calculate-estimated-mean-from-grouped-data compare-distributions-using-averages compare-distributions-using-spread','9.4':'draw-frequency-polygon interpret-frequency-polygon','9.6':'draw-cumulative-frequency-graph interpret-cumulative-frequency-graph estimate-median-from-cumulative-frequency-graph estimate-quartiles-from-cumulative-frequency-graph draw-box-plot interpret-box-plot compare-distributions-using-box-plots','9.7':'calculate-frequency-density draw-histogram interpret-histogram'
}
GROUP_NAMES={'1':'number-skills','2':'algebra-and-graphs-skills','3':'coordinate-geometry-skills','4':'geometry-skills','5':'mensuration-skills','6':'trigonometry-skills','7':'transformations-and-vectors-skills','8':'probability-skills','9':'statistics-skills'}
def words(s): return s.split()
def label(s): return s.replace('-',' ').capitalize()
def description(s):
 a,*obj=s.split('-'); thing=' '.join(obj)
 templates={'identify':'Recognise and name {x} from its defining mathematical properties.','recognise':'Recognise {x} from its mathematical form or defining properties.','calculate':'Determine {x} accurately from the supplied values and relationships.','find':'Determine {x} by applying the appropriate mathematical procedure.','apply':'Use {x} to obtain or justify a required mathematical result.','use':'Use {x} correctly to perform the stated mathematical task.','convert':'Change between {x} while preserving the represented quantity.','solve':'Determine all values satisfying {x} and check the applicable conditions.','draw':'Construct an accurate {x} from the supplied mathematical information.','plot':'Plot {x} accurately using suitable coordinates and scales.','interpret':'Extract and explain mathematical information represented by {x}.','construct':'Construct {x} accurately using the specified mathematical instruments or data.','classify':'Classify {x} using its defining mathematical properties.','compare':'Compare {x} using the relevant values, symbols, or measures.','represent':'Represent {x} using the required mathematical notation or diagram.','simplify':'Rewrite {x} in an equivalent simplest form.','factorise':'Rewrite {x} as a product of appropriate factors.','expand':'Remove brackets from {x} while preserving algebraic equivalence.','estimate':'Obtain a justified approximate value for {x}.','round':'Round {x} to the stated degree of accuracy.','evaluate':'Evaluate {x} by substituting and calculating correctly.','differentiate':'Find the derivative of {x} using the applicable differentiation rule.','prove':'Establish {x} through a valid sequence of mathematical deductions.','read':'Read {x} accurately from the given representation.','form':'Form {x} from the stated proportional relationship.','sketch':'Sketch {x} showing its essential mathematical features.','recall':'Recall {x} exactly for use without calculator derivation.','choose':'Choose {x} by matching the measure to the data and purpose.','preserve':'Preserve {x} so premature rounding does not alter the final result.'}
 templates.update({'add':'Combine {x} component-wise or arithmetically to obtain the required result.','change':'Rearrange {x} while preserving the equality represented by the formula.','collect':'Combine {x} by adding or subtracting their coefficients.','complete':'Rewrite {x} in completed-square form by balancing the constant term.','continue':'Extend {x} by applying its established term-to-term pattern.','describe':'State {x} completely using the required parameters and mathematical vocabulary.','design':'Construct {x} so its questions and response options collect usable unbiased data.','divide':'Partition {x} according to the stated ratio while preserving the total.','enlarge':'Map every point of {x} from the centre using the stated scale factor.','enter':'Enter {x} in a calculator using a form that preserves its numerical value.','express':'Rewrite {x} in the requested percentage or mathematical form.','model':'Represent {x} with a repeated multiplicative relationship over time.','multiply':'Scale {x} by multiplying each component by the stated scalar.','order':'Arrange {x} from least to greatest or greatest to least using their values.','rationalise':'Remove surds from {x} by multiplying by a suitable equivalent expression.','reflect':'Map {x} across the stated mirror line at equal perpendicular distances.','rotate':'Map {x} about the stated centre through the given angle and direction.','substitute':'Replace variables in {x} with supplied values and evaluate correctly.','subtract':'Find the vector or numerical difference for {x} using the applicable subtraction rule.','translate':'Map every point of {x} by the stated translation vector.'})
 return templates.get(a,'Carry out {x} using its defining mathematical rule and verify the resulting representation.').format(x=thing)
def main():
 points=json.loads((TAX/'syllabus-points.json').read_text(encoding='utf-8'))['syllabusPoints']; pointmap={}; used=set()
 for p in points:
  if p.get('extendedOnlyPlaceholder'): continue
  key=p['id'][1:]; ids=words(COMMON.get(key,''))
  if p['tier']=='extended': ids+=words(EXT.get(key,''))
  if not ids: raise SystemExit(f'No curated decomposition for {p["id"]}')
  group=GROUP_NAMES[key.split('.')[0]]; pointmap[p['id']]={'skillGroupIds':[group],'atomicSkills':ids,'unmappedClauses':[],'reviewNotes':'Explicit Gate 1C pedagogical decomposition.'}; used.update(ids)
 defs={s:{'label':label(s),'description':description(s),'action':s.split('-')[0],'conceptIds':[x for x in s.split('-')[1:] if x not in {'a','an','and','from','in','of','on','the','to','using','with'}],'skillGroupIds':[GROUP_NAMES[next(pid[1] for pid,v in pointmap.items() if s in v['atomicSkills'])]],'relativeLevel':2 if s.startswith(('solve','prove','differentiate')) else 1,'prerequisiteSkillIds':[],'relatedSkillIds':[]} for s in sorted(used)}
 prereq={'apply-four-operations-with-integers':'identify-integers','solve-simultaneous-linear-equations':'solve-linear-equation','calculate-estimated-mean-from-grouped-data':'calculate-mean','solve-three-dimensional-trigonometry-problem':'find-side-in-right-triangle','apply-centre-circumference-angle-theorem':'apply-angle-sum-of-triangle','solve-quadratic-equation-by-factorisation':'factorise-quadratic-expression','calculate-frequency-density':'calculate-with-fractions'}
 for child,parent in prereq.items():
  if child in defs and parent in defs: defs[child]['prerequisiteSkillIds'].append(parent)
 CONFIG.mkdir(exist_ok=True); (CONFIG/'0580-atomic-skills.json').write_text(json.dumps({'schemaVersion':'1.0','syllabusCode':'0580','taxonomyVersion':'0580-2025-2027-v1','points':pointmap},indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); (CONFIG/'0580-skill-definitions.json').write_text(json.dumps({'schemaVersion':'1.0','skills':defs},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print(f'Curated {len(pointmap)} non-placeholder points and {len(defs)} atomic skills')
if __name__=='__main__': main()
