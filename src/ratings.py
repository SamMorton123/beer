import numpy as np

class RatingsMetadata:
    """Container for metadata from rating calculations"""
    def __init__(self):
        self.confidence_interval = None
        self.percentile = None
        self.z_score = None
        self.components = {}
        self.global_context = None
        self.interpretation = None


class BeerRater:
    def __init__(self):
        
        self.adjustment_strength = 0.65
        self.bounding_factor = 0.3

        self.use_robust_stats = True
        self.min_sample_size = 5
        self.outlier_threshold = 3

        self.recency_half_life = 30
        self.enable_recency_weighting = False

        self.extreme_compression_factor = 0.6

        self.use_bayesian_shrinkage = True
        self.use_adaptive_smoothing = True

        self.metadata = RatingsMetadata()

    def scale(self, raw_rating, style_ratings, all_user_ratings = None):
        """
        Main scaling function

        - raw_rating
        - style_ratings: array of raw ratings for the beer's style
        - all_user_ratings: all user beer ratings, defaults to None
        """

        if not self._validateInputs(raw_rating, style_ratings):
            return self._getDefaultResult(raw_rating)
        
        N = len(style_ratings)
        
        rating_stats = self._calculateStats(style_ratings)

        global_context = None
        if all_user_ratings is not None:
            global_context = self._calculateGlobalContext(all_user_ratings, rating_stats['mean'])
        
        # Bayesian shrinkage for small samples
        adjusted_stats = (
            self._applyShrinkage(rating_stats, global_context, N)
            if self.use_bayesian_shrinkage and global_context is not None
            else rating_stats
        )

        # Get z score
        z_score = (raw_rating - adjusted_stats['mean']) / adjusted_stats['std'] if adjusted_stats['std'] > 0 else 0

        confidence = self._calculateConfidence(adjusted_stats, N)
        
        variance_influence = self._calculateVarianceInfluence(adjusted_stats['variance'])

        # Extreme rating modifier (compress adjustments near boundaries)
        extreme_rating_modifier = self._calculateExtremeModifier(raw_rating)

        # Outlier dampening (diminishing returns for extreme z-scores)
        outlier_dampening = self._calculateOutlierDampening(z_score)

        smoothing_constant = self._calculateAdaptiveSmoothing(N) if self.use_adaptive_smoothing else 2.0

        # Base adjustment using tanh for smooth bounded scaling
        max_adjustment = raw_rating * self.bounding_factor
        base_adjustment = np.tanh(z_score / smoothing_constant) * max_adjustment

        # Composite final adjustment
        final_adjustment = base_adjustment * self.adjustment_strength * variance_influence * confidence * extreme_rating_modifier * outlier_dampening

        scaled_rating = self._clamp(raw_rating + final_adjustment, 1, 10)

        # Store metadata
        self.metadata.z_score = round(z_score, 2)
        self.metadata.confidence_interval = self._calculateConfidenceInterval(scaled_rating, adjusted_stats, N)
        self.metadata.percentile = self._calculatePercentile(raw_rating, style_ratings)
        self.metadata.components = {
            'variance_influence': round(variance_influence, 3),
            'extreme_modifier': round(extreme_rating_modifier, 3),
            'outlier_dampening': round(outlier_dampening, 3),
            'smoothing_constant': round(smoothing_constant, 2)
        }
        self.metadata.global_context = global_context

        return round(scaled_rating, 2)
    
    def _validateInputs(self, raw_rating, style_ratings):
        if not isinstance(raw_rating, (int, float)) or raw_rating < 1 or raw_rating > 10:
            print('Invalid raw rating:', raw_rating)
            return False
        
        if not isinstance(style_ratings, list) or len(style_ratings) == 0:
            print('Invalid category ratings:', style_ratings)
            return False
        
        return True
    
    def _calculateStats(self, style_ratings, robust_stats_threshold = 3):
        if self.use_robust_stats and len(style_ratings) >= robust_stats_threshold:
            return self._calculateRobustStats(style_ratings)

        return self._calculateClassicalStats(style_ratings)

    def _calculateRobustStats(self, style_ratings):
        ratings_array = np.array(style_ratings)
        median = np.median(ratings_array)

        # Median absolute deviation (MAD)
        absolute_deviations = np.abs(ratings_array - median)
        mad = np.median(absolute_deviations)

        # Convert MAD to standard deviation equivalent
        std = mad * 1.4826
        variance = std ** 2

        return {
            'mean': median,  # Use median as robust mean estimate
            'median': median,
            'std': std,
            'variance': variance,
            'mad': mad,
            'robust': True
        }
    
    def _calculateClassicalStats(self, style_ratings):
        ratings_array = np.array(style_ratings)
        return {
            'mean': np.mean(ratings_array),
            'median': np.median(ratings_array),
            'std': np.std(ratings_array),
            'variance': np.var(ratings_array),
            'robust': False
        }

    def _calculateGlobalContext(self, all_user_ratings, category_mean):
        global_mean = np.mean(all_user_ratings)
        category_deviation = category_mean - global_mean

        if category_deviation > 1.5:
            interpretation = "You love this style"
        elif category_deviation > 0.5:
            interpretation = "You enjoy this style"
        elif category_deviation < -1.5:
            interpretation = "This isn't your preferred style"
        elif category_deviation < -0.5:
            interpretation = "You're less fond of this style"
        else:
            interpretation = "You're neutral on this style"

        return {
            'global_mean': round(global_mean, 2),
            'category_deviation': round(category_deviation, 2),
            'interpretation': interpretation
        }
    
    def _applyShrinkage(self, rating_stats, global_context, N):
        if N >= self.min_sample_size or global_context is None:
            new_rating_stats = {key: rating_stats[key] for key in rating_stats}
            new_rating_stats['shrinkage_applied'] = False
            new_rating_stats['shrinkage_factor'] = None
            return new_rating_stats
        
        # Bayesian shrinkage toward global mean
        # More shrinkage with smaller sample sizes
        shrinkage_factor = N / self.min_sample_size
        global_mean = global_context['global_mean']
        shrunk_mean = shrinkage_factor * rating_stats['mean'] + (1 - shrinkage_factor) * global_mean

        shrunk_stats = {key: rating_stats[key] for key in rating_stats}
        shrunk_stats['mean'] = shrunk_mean
        shrunk_stats['shrinkage_applied'] = True
        shrunk_stats['shrinkage_factor'] = round(shrinkage_factor, 2)

        return shrunk_stats
    
    def _calculateConfidence(self, rating_stats, N):
        sample_size_component = min(1.0, N / self.min_sample_size)

        mean_in_use = rating_stats['mean'] if rating_stats['mean'] != 0 else 1
        cv = rating_stats['std'] / mean_in_use
        precision_component = 1 / (1 + cv)

        combined_confidence = sample_size_component * precision_component
        return self._clamp(combined_confidence, 0, 1)
    
    def _calculateVarianceInfluence(self, variance):
        """
        Sigmoid function centered at variance = 1.0
        Low variance (< 0.5): minimal influence (~0.2)
        High variance (> 2): maximum influence (~0.95)
        """
        return 1 / (1 + np.exp(-3 * (variance - 1.0)))
    
    def _calculateExtremeModifier(self, rating):
        """
        Reduce adjustments for ratings near boundaries (1 or 10)
        to preserve the meaningfulness of extreme ratings
        """
        distance_from_boundary = min(rating - 1, 10 - rating)
        
        if distance_from_boundary >= 2:
            return 1.0  # Full adjustment for mid-range ratings
        
        # Smooth compression near boundaries
        return (distance_from_boundary / 2) ** self.extreme_compression_factor
    
    def _calculateOutlierDampening(self, z_score):
        """
        Apply diminishing returns for extreme z-scores
        z=3 → ~0.77, z=4 → ~0.63
        """
        abs_z = abs(z_score)
        
        if abs_z <= 2:
            return 1.0  # No dampening for typical ratings
        
        # Diminishing returns for extreme z-scores
        return 1 / (1 + 0.3 * (abs_z - 2))
    
    def _calculateAdaptiveSmoothing(self, N):
        """
        Smaller samples get more smoothing (higher constant)
        Larger samples get less smoothing (lower constant)
        """
        base_smoothness = 2.5
        min_smoothness = 1.5
        
        factor = max(0, 1 - N / 20)
        return min_smoothness + factor * (base_smoothness - min_smoothness)
    
    def _calculateConfidenceInterval(self, scaled_rating, rating_stats, N):
        """
        Calculate 95% confidence interval
        Width decreases with sample size
        """
        standard_error = rating_stats['std'] / np.sqrt(N)
        margin_of_error = 1.96 * standard_error
        
        lower = self._clamp(scaled_rating - margin_of_error, 1, 10)
        upper = self._clamp(scaled_rating + margin_of_error, 1, 10)
        width = upper - lower
        
        return {
            'lower': round(lower, 2),
            'upper': round(upper, 2),
            'width': round(width, 2)
        }
    
    def _calculatePercentile(self, rating, style_ratings):
        """
        Calculate percentile with proper tie handling
        Uses average rank method for ties
        """
        ratings_array = np.array(style_ratings)
        
        count_below = np.sum(ratings_array < rating)
        count_equal = np.sum(ratings_array == rating)
        
        # Average rank for ties
        average_rank = count_below + (count_equal + 1) / 2
        percentile = (average_rank / len(ratings_array)) * 100
        
        return round(percentile, 1)
    
    def _clamp(self, value, min_val=1, max_val=10):
        """Clamp value between min and max"""
        return max(min_val, min(max_val, value))
    
    def _getDefaultResult(self, raw_rating):
        """Return default result for invalid inputs"""
        self.metadata.confidence_interval = {'lower': raw_rating, 'upper': raw_rating, 'width': 0}
        self.metadata.percentile = 0
        self.metadata.z_score = 0
        self.metadata.components = {}
        self.metadata.global_context = None
        return raw_rating
